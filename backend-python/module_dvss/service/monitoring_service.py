"""
系统监控与动态阈值计算模块
负责监控系统负载并计算分片阈值k
"""
import yaml
import psutil
import redis
import asyncio
import logging
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """系统指标数据类"""
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    active_connections: int
    timestamp: datetime

@dataclass
class LoadScore:
    """负载分数数据类"""
    score: float
    level: str
    components: Dict[str, float]

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, config_path: str = "/app/config/thresholds.yaml", 
                 redis_client=None):
        self.config_path = config_path
        self.redis_client = redis_client
        self.config = {}
        self.load_config()
        
        # 历史数据存储
        self.metrics_history = []
        self.max_history_size = 100
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded threshold config from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self._set_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_default_config()
    
    def _set_default_config(self):
        """设置默认配置"""
        self.config = {
            'dynamic_threshold': {
                'coefficients': {'alpha': 0.3, 'beta': 0.5, 'gamma': 2},
                'load_weights': {
                    'cpu_usage': 0.3, 'memory_usage': 0.25, 'disk_io': 0.2,
                    'network_io': 0.15, 'active_connections': 0.1
                },
                'load_thresholds': {'low': 0.3, 'medium': 0.6, 'high': 0.8, 'critical': 0.9},
                'k_range': {'min': 2, 'max': 10, 'default': 3}
            }
        }
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1.0) / 100.0
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent / 100.0
            
            # 磁盘IO
            disk_io = self._get_disk_io_rate()
            
            # 网络IO
            network_io = self._get_network_io_rate()
            
            # 活跃连接数
            active_connections = len(psutil.net_connections())
            
            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_io=disk_io,
                network_io=network_io,
                active_connections=active_connections,
                timestamp=datetime.now()
            )
            
            # 存储历史数据
            self._store_metrics_history(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            # 返回默认值
            return SystemMetrics(0.0, 0.0, 0.0, 0.0, 0, datetime.now())
    
    def _get_disk_io_rate(self) -> float:
        """获取磁盘IO使用率"""
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                # 简化计算：基于读写字节数
                total_bytes = disk_io.read_bytes + disk_io.write_bytes
                # 假设基准为1GB/s
                baseline = 1024 * 1024 * 1024
                return min(total_bytes / baseline, 1.0)
            return 0.0
        except:
            return 0.0
    
    def _get_network_io_rate(self) -> float:
        """获取网络IO使用率"""
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                # 简化计算：基于收发字节数
                total_bytes = net_io.bytes_sent + net_io.bytes_recv
                # 假设基准为100MB/s
                baseline = 100 * 1024 * 1024
                return min(total_bytes / baseline, 1.0)
            return 0.0
        except:
            return 0.0
    
    def _store_metrics_history(self, metrics: SystemMetrics):
        """存储指标历史"""
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
    
    def calculate_load_score(self, metrics: SystemMetrics) -> LoadScore:
        """
        计算系统负载分数
        
        Args:
            metrics: 系统指标
            
        Returns:
            负载分数和等级
        """
        weights = self.config['dynamic_threshold']['load_weights']
        
        # 计算各组件分数
        components = {
            'cpu': metrics.cpu_usage * weights['cpu_usage'],
            'memory': metrics.memory_usage * weights['memory_usage'],
            'disk_io': metrics.disk_io * weights['disk_io'],
            'network_io': metrics.network_io * weights['network_io'],
            'connections': min(metrics.active_connections / 1000, 1.0) * weights['active_connections']
        }
        
        # 总分数
        total_score = sum(components.values())
        total_score = min(max(total_score, 0.0), 1.0)
        
        # 确定负载等级
        thresholds = self.config['dynamic_threshold']['load_thresholds']
        if total_score >= thresholds['critical']:
            level = 'critical'
        elif total_score >= thresholds['high']:
            level = 'high'
        elif total_score >= thresholds['medium']:
            level = 'medium'
        else:
            level = 'low'
        
        return LoadScore(
            score=total_score,
            level=level,
            components=components
        )
    
    def get_historical_average(self, window_minutes: int = 10) -> float:
        """获取历史平均负载"""
        if not self.metrics_history:
            return 0.0
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return 0.0
        
        scores = [self.calculate_load_score(m).score for m in recent_metrics]
        return np.mean(scores)
    
    async def store_metrics_to_redis(self, metrics: SystemMetrics, load_score: LoadScore):
        """将指标存储到Redis"""
        if not self.redis_client:
            return
        
        try:
            # 存储当前负载分数
            await self.redis_client.set(
                self.config.get('cache', {}).get('system_load_key', 'system_load'),
                load_score.score,
                ex=self.config.get('cache', {}).get('ttl', 300)
            )
            
            # 存储详细指标
            metrics_data = {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'disk_io': metrics.disk_io,
                'network_io': metrics.network_io,
                'active_connections': metrics.active_connections,
                'load_score': load_score.score,
                'load_level': load_score.level,
                'timestamp': metrics.timestamp.isoformat()
            }
            
            await self.redis_client.hset(
                'system_metrics:current',
                mapping=metrics_data
            )
            
        except Exception as e:
            logger.error(f"Error storing metrics to Redis: {e}")

class DynamicThresholdCalculator:
    """动态阈值计算器"""
    
    def __init__(self, config_path: str = "/app/config/thresholds.yaml", 
                 redis_client=None):
        self.config_path = config_path
        self.redis_client = redis_client
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_default_config()
    
    def _set_default_config(self):
        """设置默认配置"""
        self.config = {
            'dynamic_threshold': {
                'coefficients': {'alpha': 0.3, 'beta': 0.5, 'gamma': 2},
                'k_range': {'min': 2, 'max': 10, 'default': 3}
            }
        }
    
    def calculate_k(self, load_score: float, sensitivity_score: float) -> int:
        """
        计算动态阈值k
        公式: k = α·L + β·S + γ
        
        Args:
            load_score: 系统负载分数 (0-1)
            sensitivity_score: 数据敏感度分数 (0-1)
            
        Returns:
            计算得到的k值
        """
        coeffs = self.config['dynamic_threshold']['coefficients']
        alpha = coeffs['alpha']
        beta = coeffs['beta']
        gamma = coeffs['gamma']
        
        # 计算k值
        k_float = alpha * load_score + beta * sensitivity_score + gamma
        
        # 确保k在合理范围内
        k_range = self.config['dynamic_threshold']['k_range']
        k = max(k_range['min'], min(int(round(k_float)), k_range['max']))
        
        return k
    
    async def get_current_k(self, sensitivity_score: float = None) -> int:
        """
        获取当前k值
        
        Args:
            sensitivity_score: 特定数据的敏感度分数
            
        Returns:
            当前k值
        """
        try:
            # 从Redis获取当前系统负载
            if self.redis_client:
                load_score_str = await self.redis_client.get(
                    self.config.get('cache', {}).get('system_load_key', 'system_load')
                )
                if load_score_str:
                    load_score = float(load_score_str)
                else:
                    load_score = 0.3  # 默认负载
            else:
                load_score = 0.3
            
            # 如果没有提供敏感度分数，使用默认值
            if sensitivity_score is None:
                sensitivity_score = 0.6  # 中等敏感度
            
            k = self.calculate_k(load_score, sensitivity_score)
            
            # 缓存计算结果
            if self.redis_client:
                await self.redis_client.set(
                    self.config.get('cache', {}).get('current_k_key', 'current_k'),
                    k,
                    ex=self.config.get('cache', {}).get('ttl', 300)
                )
            
            return k
            
        except Exception as e:
            logger.error(f"Error calculating current k: {e}")
            return self.config['dynamic_threshold']['k_range']['default']
    
    def get_k_recommendation(self, load_score: float, sensitivity_score: float) -> Dict[str, Any]:
        """
        获取k值推荐和解释
        
        Args:
            load_score: 系统负载分数
            sensitivity_score: 敏感度分数
            
        Returns:
            k值推荐信息
        """
        k = self.calculate_k(load_score, sensitivity_score)
        
        # 生成解释
        explanation = []
        
        if load_score > 0.8:
            explanation.append("系统负载较高，增加分片阈值以提高安全性")
        elif load_score < 0.3:
            explanation.append("系统负载较低，可适度降低分片阈值")
        
        if sensitivity_score > 0.8:
            explanation.append("数据敏感度很高，建议使用较高的分片阈值")
        elif sensitivity_score < 0.4:
            explanation.append("数据敏感度较低，可使用较低的分片阈值")
        
        return {
            'recommended_k': k,
            'load_score': load_score,
            'sensitivity_score': sensitivity_score,
            'explanation': explanation,
            'security_level': self._get_security_level(k),
            'performance_impact': self._get_performance_impact(k)
        }
    
    def _get_security_level(self, k: int) -> str:
        """根据k值获取安全等级"""
        if k >= 7:
            return 'very_high'
        elif k >= 5:
            return 'high'
        elif k >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _get_performance_impact(self, k: int) -> str:
        """根据k值获取性能影响"""
        if k >= 7:
            return 'high_overhead'
        elif k >= 5:
            return 'medium_overhead'
        elif k >= 3:
            return 'low_overhead'
        else:
            return 'minimal_overhead'

class MonitoringService:
    """监控服务主类"""
    
    def __init__(self, config_path: str = "/app/config/thresholds.yaml", 
                 redis_client=None):
        self.monitor = SystemMonitor(config_path, redis_client)
        self.calculator = DynamicThresholdCalculator(config_path, redis_client)
        self.redis_client = redis_client
        self.running = False
    
    async def start_monitoring(self, interval: int = 30):
        """
        开始监控
        
        Args:
            interval: 监控间隔（秒）
        """
        self.running = True
        logger.info(f"Starting system monitoring with {interval}s interval")
        
        while self.running:
            try:
                # 收集系统指标
                metrics = self.monitor.collect_system_metrics()
                
                # 计算负载分数
                load_score = self.monitor.calculate_load_score(metrics)
                
                # 存储到Redis
                await self.monitor.store_metrics_to_redis(metrics, load_score)
                
                # 计算并更新当前k值
                current_k = await self.calculator.get_current_k()
                
                logger.info(f"System metrics - Load: {load_score.score:.3f} ({load_score.level}), k: {current_k}")
                
                # 等待下一次监控
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logger.info("Stopping system monitoring")
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        try:
            # 获取最新指标
            metrics = self.monitor.collect_system_metrics()
            load_score = self.monitor.calculate_load_score(metrics)
            
            # 获取当前k值
            current_k = await self.calculator.get_current_k()
            
            # 获取历史平均
            historical_avg = self.monitor.get_historical_average()
            
            return {
                'current_metrics': {
                    'cpu_usage': metrics.cpu_usage,
                    'memory_usage': metrics.memory_usage,
                    'disk_io': metrics.disk_io,
                    'network_io': metrics.network_io,
                    'active_connections': metrics.active_connections,
                    'timestamp': metrics.timestamp.isoformat()
                },
                'load_score': {
                    'current': load_score.score,
                    'level': load_score.level,
                    'components': load_score.components,
                    'historical_average': historical_avg
                },
                'threshold': {
                    'current_k': current_k,
                    'recommendation': self.calculator.get_k_recommendation(
                        load_score.score, 0.6  # 默认敏感度
                    )
                },
                'monitoring_status': {
                    'running': self.running,
                    'history_size': len(self.monitor.metrics_history)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {'error': str(e)}
