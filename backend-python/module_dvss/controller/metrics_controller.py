"""
Metrics控制器
提供Prometheus监控指标
"""

from fastapi import APIRouter

router = APIRouter()


@router.get('/metrics')
def get_metrics():
    """
    获取Prometheus指标
    """
    # 简单的metrics响应，可以后续扩展为实际的Prometheus指标
    metrics_data = """
# HELP dvss_requests_total Total number of requests
# TYPE dvss_requests_total counter
dvss_requests_total 100

# HELP dvss_errors_total Total number of errors
# TYPE dvss_errors_total counter
dvss_errors_total 0

# HELP dvss_active_users_total Number of active users
# TYPE dvss_active_users_total gauge
dvss_active_users_total 5

# HELP dvss_orders_total Total number of orders
# TYPE dvss_orders_total counter
dvss_orders_total 50

# HELP dvss_encrypted_orders_total Total number of encrypted orders
# TYPE dvss_encrypted_orders_total counter
dvss_encrypted_orders_total 25
"""

    return metrics_data.strip()
