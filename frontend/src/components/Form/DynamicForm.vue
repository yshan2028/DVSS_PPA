<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    :label-width="labelWidth"
    :label-position="labelPosition"
    :size="size"
    :disabled="disabled"
  >
    <el-row :gutter="gutter">
      <el-col
        v-for="item in formItems"
        :key="item.prop"
        :span="item.span || 24"
        :xs="item.xs"
        :sm="item.sm"
        :md="item.md"
        :lg="item.lg"
        :xl="item.xl"
      >
        <el-form-item
          :label="item.label"
          :prop="item.prop"
          :required="item.required"
          :rules="item.rules"
        >
          <!-- 输入框 -->
          <el-input
            v-if="item.type === 'input'"
            v-model="formData[item.prop]"
            :placeholder="item.placeholder"
            :disabled="item.disabled"
            :readonly="item.readonly"
            :clearable="item.clearable !== false"
            :show-password="item.showPassword"
            :maxlength="item.maxlength"
            :rows="item.rows"
            :type="item.inputType || 'text'"
          />
          
          <!-- 文本域 -->
          <el-input
            v-else-if="item.type === 'textarea'"
            v-model="formData[item.prop]"
            type="textarea"
            :placeholder="item.placeholder"
            :disabled="item.disabled"
            :readonly="item.readonly"
            :rows="item.rows || 4"
            :maxlength="item.maxlength"
            :show-word-limit="item.showWordLimit"
          />
          
          <!-- 选择器 -->
          <el-select
            v-else-if="item.type === 'select'"
            v-model="formData[item.prop]"
            :placeholder="item.placeholder"
            :disabled="item.disabled"
            :multiple="item.multiple"
            :clearable="item.clearable !== false"
            :filterable="item.filterable"
            style="width: 100%"
          >
            <el-option
              v-for="option in item.options"
              :key="option.value"
              :label="option.label"
              :value="option.value"
              :disabled="option.disabled"
            />
          </el-select>
          
          <!-- 数字输入框 -->
          <el-input-number
            v-else-if="item.type === 'number'"
            v-model="formData[item.prop]"
            :placeholder="item.placeholder"
            :disabled="item.disabled"
            :min="item.min"
            :max="item.max"
            :step="item.step"
            :precision="item.precision"
            style="width: 100%"
          />
          
          <!-- 日期选择器 -->
          <el-date-picker
            v-else-if="item.type === 'date'"
            v-model="formData[item.prop]"
            :type="item.dateType || 'date'"
            :placeholder="item.placeholder"
            :disabled="item.disabled"
            :format="item.format"
            :value-format="item.valueFormat"
            style="width: 100%"
          />
          
          <!-- 时间选择器 -->
          <el-time-picker
            v-else-if="item.type === 'time'"
            v-model="formData[item.prop]"
            :placeholder="item.placeholder"
            :disabled="item.disabled"
            :format="item.format"
            :value-format="item.valueFormat"
            style="width: 100%"
          />
          
          <!-- 开关 -->
          <el-switch
            v-else-if="item.type === 'switch'"
            v-model="formData[item.prop]"
            :disabled="item.disabled"
            :active-text="item.activeText"
            :inactive-text="item.inactiveText"
            :active-value="item.activeValue !== undefined ? item.activeValue : true"
            :inactive-value="item.inactiveValue !== undefined ? item.inactiveValue : false"
          />
          
          <!-- 单选框组 -->
          <el-radio-group
            v-else-if="item.type === 'radio'"
            v-model="formData[item.prop]"
            :disabled="item.disabled"
          >
            <el-radio
              v-for="option in item.options"
              :key="option.value"
              :label="option.value"
              :disabled="option.disabled"
            >
              {{ option.label }}
            </el-radio>
          </el-radio-group>
          
          <!-- 多选框组 -->
          <el-checkbox-group
            v-else-if="item.type === 'checkbox'"
            v-model="formData[item.prop]"
            :disabled="item.disabled"
          >
            <el-checkbox
              v-for="option in item.options"
              :key="option.value"
              :label="option.value"
              :disabled="option.disabled"
            >
              {{ option.label }}
            </el-checkbox>
          </el-checkbox-group>
          
          <!-- 文件上传 -->
          <el-upload
            v-else-if="item.type === 'upload'"
            :action="item.action"
            :headers="item.headers"
            :data="item.data"
            :name="item.name || 'file'"
            :multiple="item.multiple"
            :accept="item.accept"
            :limit="item.limit"
            :file-list="formData[item.prop]"
            :disabled="item.disabled"
            :before-upload="item.beforeUpload"
            :on-success="(response, file, fileList) => handleUploadSuccess(response, file, fileList, item.prop)"
            :on-error="item.onError"
            :on-remove="(file, fileList) => handleUploadRemove(file, fileList, item.prop)"
          >
            <el-button :icon="Upload">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip" v-if="item.tip">
                {{ item.tip }}
              </div>
            </template>
          </el-upload>
          
          <!-- 自定义插槽 -->
          <slot
            v-else-if="item.type === 'slot'"
            :name="item.prop"
            :item="item"
            :value="formData[item.prop]"
          />
        </el-form-item>
      </el-col>
    </el-row>
    
    <!-- 表单操作按钮 -->
    <el-form-item v-if="showActions" class="form-actions">
      <slot name="actions">
        <el-button @click="handleReset" v-if="showReset">
          重置
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ submitText }}
        </el-button>
      </slot>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Upload } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  // 表单数据
  modelValue: {
    type: Object,
    default: () => ({})
  },
  // 表单项配置
  formItems: {
    type: Array,
    required: true
  },
  // 表单规则
  rules: {
    type: Object,
    default: () => ({})
  },
  // 表单属性
  labelWidth: {
    type: String,
    default: '120px'
  },
  labelPosition: {
    type: String,
    default: 'right'
  },
  size: {
    type: String,
    default: 'default'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  // 栅格间距
  gutter: {
    type: Number,
    default: 20
  },
  // 操作按钮
  showActions: {
    type: Boolean,
    default: true
  },
  showReset: {
    type: Boolean,
    default: true
  },
  submitText: {
    type: String,
    default: '提交'
  },
  submitLoading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'submit', 'reset'])

// 表单引用
const formRef = ref()

// 表单数据
const formData = reactive({})

// 表单规则
const formRules = reactive({})

// 初始化表单数据
const initFormData = () => {
  // 清空现有数据
  Object.keys(formData).forEach(key => {
    delete formData[key]
  })
  
  // 从配置初始化默认值
  props.formItems.forEach(item => {
    if (item.defaultValue !== undefined) {
      formData[item.prop] = item.defaultValue
    } else {
      // 根据类型设置默认值
      switch (item.type) {
        case 'checkbox':
          formData[item.prop] = []
          break
        case 'number':
          formData[item.prop] = undefined
          break
        case 'switch':
          formData[item.prop] = item.inactiveValue !== undefined ? item.inactiveValue : false
          break
        case 'upload':
          formData[item.prop] = []
          break
        default:
          formData[item.prop] = undefined
      }
    }
  })
  
  // 合并传入的数据
  Object.assign(formData, props.modelValue)
}

// 初始化表单规则
const initFormRules = () => {
  // 清空现有规则
  Object.keys(formRules).forEach(key => {
    delete formRules[key]
  })
  
  // 从配置生成规则
  props.formItems.forEach(item => {
    if (item.rules) {
      formRules[item.prop] = item.rules
    } else if (item.required) {
      formRules[item.prop] = [
        { required: true, message: `请输入${item.label}`, trigger: 'blur' }
      ]
    }
  })
  
  // 合并传入的规则
  Object.assign(formRules, props.rules)
}

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  Object.assign(formData, newVal)
}, { deep: true })

// 监听表单数据变化
watch(formData, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

// 初始化
initFormData()
initFormRules()

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    emit('submit', formData)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 重置表单
const handleReset = () => {
  formRef.value.resetFields()
  emit('reset')
}

// 验证表单
const validate = () => {
  return formRef.value.validate()
}

// 验证指定字段
const validateField = (prop) => {
  return formRef.value.validateField(prop)
}

// 清空验证结果
const clearValidate = () => {
  formRef.value.clearValidate()
}

// 处理文件上传成功
const handleUploadSuccess = (response, file, fileList, prop) => {
  formData[prop] = fileList
}

// 处理文件移除
const handleUploadRemove = (file, fileList, prop) => {
  formData[prop] = fileList
}

// 暴露方法
defineExpose({
  validate,
  validateField,
  clearValidate,
  resetFields: handleReset
})
</script>

<style scoped>
.form-actions {
  text-align: center;
  margin-top: 20px;
}

.form-actions .el-button {
  margin: 0 10px;
}
</style>
