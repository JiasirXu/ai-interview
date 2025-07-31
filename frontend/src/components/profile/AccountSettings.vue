<template>
  <div class="account-settings">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item">个人中心</span>
      <span class="breadcrumb-separator">></span>
      <span class="breadcrumb-item current">账号设置</span>
    </div>

    <!-- 安全设置 -->
    <div class="settings-section">
      <h2 class="section-title">安全设置</h2>
      
      <!-- 密码修改 -->
      <div class="setting-item">
        <div class="item-info">
          <div class="item-icon">
            <SvgIcon name="lock" />
          </div>
          <div class="item-content">
            <div class="item-title">密码修改</div>
            <div class="item-desc">最后修改时间：{{ lastPasswordChangeTime }}</div>
          </div>
        </div>
        <button class="action-btn secondary" @click="openPasswordModal">修改密码</button>
      </div>

      <!-- 手机绑定 -->
      <div class="setting-item">
        <div class="item-info">
          <div class="item-icon">
            <SvgIcon name="container1" />
          </div>
          <div class="item-content">
            <div class="item-title">手机绑定</div>
            <div class="item-desc">已绑定：{{ maskedPhone }}</div>
          </div>
        </div>
        <button class="action-btn secondary" @click="openPhoneModal">更换手机</button>
      </div>

      <!-- 登录历史 -->
      <div class="setting-item">
        <div class="item-info">
          <div class="item-icon">
            <SvgIcon name="container2" />
          </div>
          <div class="item-content">
            <div class="item-title">登录历史</div>
            <div class="item-desc">当前时间：{{ currentDateTime }}</div>
          </div>
        </div>
        <button class="action-btn secondary" @click="toggleLoginHistoryPanel">
          登录历史
        </button>
      </div>

      <!-- 登录历史记录面板 -->
      <div class="login-history-panel" v-if="showLoginHistoryPanel">
        <div class="history-content">
          <div class="history-header">
            <h4>登录历史记录</h4>
            <p>最近的登录活动记录</p>
          </div>
          <div class="history-list">
            <div class="history-item-detailed" v-for="record in loginHistoryRecords" :key="record.id">
              <div class="history-info-detailed">
                <div class="history-time-detailed">{{ record.loginTime }}</div>
                <div class="history-details">
                  <span class="history-ip">{{ record.ipAddress }}</span>
                  <span class="history-location">{{ record.location }}</span>
                  <span class="history-device">{{ record.device }}</span>
                </div>
              </div>
              <div class="history-status" :class="record.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ record.statusText }}</span>
              </div>
            </div>
          </div>
        
        </div>
      </div>
    </div>

    <!-- 隐私控制 -->
    <div class="settings-section">
      <h2 class="section-title">隐私控制</h2>

      <!-- 数据共享授权 -->
      <div class="setting-item">
        <div class="item-info">
          <div class="item-icon">
            <SvgIcon name="container3" />
          </div>
          <div class="item-content">
            <div class="item-title">数据共享授权</div>
            <div class="item-desc">您的匿名信息将用于改进试验模型</div>
          </div>
        </div>
        <div class="toggle-switch" :class="{ active: privacySettings.dataSharing }" @click="toggleDataSharing">
          <div class="toggle-slider"></div>
        </div>
      </div>

      <!-- 简历可见范围 -->
      <div class="setting-item">
        <div class="item-info">
          <div class="item-icon">
            <SvgIcon name="container4" />
          </div>
          <div class="item-content">
            <div class="item-title">简历可见范围</div>
            <div class="item-desc">设置您的简历对哪些人可见</div>
          </div>
        </div>
        <button class="action-btn secondary" @click="openResumeVisibilityModal">修改设置</button>
      </div>

      <!-- 痕迹清除 -->
      <div class="setting-item">
        <div class="item-info">
          <div class="item-icon">
            <SvgIcon name="container5" />
          </div>
          <div class="item-content">
            <div class="item-title">痕迹清除</div>
            <div class="item-desc">清除所有面试记录和评估历史</div>
          </div>
        </div>
        <button class="action-btn secondary" @click="clearUserTraces">清除痕迹</button>
      </div>
    </div>

    <!-- 账号注销 -->
    <div class="settings-section delete-section">
      <div class="delete-section-header" @click="isDeleteSectionVisible = !isDeleteSectionVisible">
        <h2 class="section-title delete-title">账号注销</h2>
        <span class="collapse-indicator">{{ isDeleteSectionVisible ? '收起' : '展开' }}</span>
      </div>
      
      <div v-if="isDeleteSectionVisible" class="delete-content">
        <div class="warning-notice delete-warning">
          <div class="warning-icon">⚠️</div>
          <div class="warning-text">注销账号将清除以下数据：</div>
        </div>

        <ul class="data-list delete-data-list">
          <li>所有面试记录</li>
          <li>技能评估历史</li>
          <li>聊天记录</li>
          <li>个人资料信息</li>
        </ul>

        <div class="form-group delete-form-group">
          <label class="form-label delete-form-label">注销原因</label>
          <select class="form-select delete-form-select" v-model="cancelReason">
            <option value="">请选择注销原因</option>
            <option value="不再使用">不再使用该服务</option>
            <option value="功能不满意">功能不满意</option>
            <option value="隐私担忧">隐私安全担忧</option>
            <option value="其他">其他原因</option>
          </select>
        </div>

        <div class="form-group delete-form-group">
          <label class="checkbox-container delete-checkbox">
            <input type="checkbox" v-model="confirmDelete">
            <span class="checkmark"></span>
            我已知晓所有数据将永久删除
          </label>
        </div>

        <button class="action-btn danger delete-btn" :disabled="!confirmDelete || !cancelReason" @click="deleteAccountHandler">
          注销账号
        </button>
      </div>
    </div>

    <!-- 密码修改模态框 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="closePasswordModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">当前密码</label>
            <input 
              type="password" 
              v-model="passwordForm.currentPassword" 
              placeholder="请输入当前密码"
              class="form-input"
              :class="{ error: errors.currentPassword }"
            />
            <span v-if="errors.currentPassword" class="error-text">{{ errors.currentPassword }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.newPassword" 
              placeholder="请输入新密码"
              class="form-input"
              :class="{ error: errors.newPassword }"
            />
            <span v-if="errors.newPassword" class="error-text">{{ errors.newPassword }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.confirmPassword" 
              placeholder="请再次输入新密码"
              class="form-input"
              :class="{ error: errors.confirmPassword }"
            />
            <span v-if="errors.confirmPassword" class="error-text">{{ errors.confirmPassword }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="action-btn secondary" @click="closePasswordModal">取消</button>
          <button class="action-btn primary" @click="changePassword" :disabled="saving">
            {{ saving ? '修改中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 手机更换模态框 -->
    <div v-if="showPhoneModal" class="modal-overlay" @click="closePhoneModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>更换手机号</h3>
          <button class="close-btn" @click="closePhoneModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">新手机号</label>
            <input 
              type="tel" 
              v-model="phoneForm.newPhone" 
              placeholder="请输入新手机号"
              class="form-input"
              :class="{ error: errors.newPhone }"
              maxlength="11"
            />
            <span v-if="errors.newPhone" class="error-text">{{ errors.newPhone }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="action-btn secondary" @click="closePhoneModal">取消</button>
          <button class="action-btn primary" @click="changePhone" :disabled="saving">
            {{ saving ? '更换中...' : '确认更换' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 简历可见范围模态框 -->
    <div v-if="showResumeVisibilityModal" class="modal-overlay" @click="closeResumeVisibilityModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>简历可见范围设置</h3>
          <button class="close-btn" @click="closeResumeVisibilityModal">×</button>
        </div>
        <div class="modal-body">
          <div class="visibility-options">
            <label class="radio-option">
              <input type="radio" v-model="resumeVisibility" value="public" />
              <span class="radio-label">公开</span>
              <span class="radio-desc">所有人都可以查看您的简历</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="resumeVisibility" value="limited" />
              <span class="radio-label">有限公开</span>
              <span class="radio-desc">只有通过搜索匹配的HR可以查看</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="resumeVisibility" value="private" />
              <span class="radio-label">私密</span>
              <span class="radio-desc">只有您主动投递的职位HR可以查看</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="action-btn secondary" @click="closeResumeVisibilityModal">取消</button>
          <button class="action-btn primary" @click="saveResumeVisibility" :disabled="saving">
            {{ saving ? '保存中...' : '保存设置' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from '@/components/common/SvgIcon.vue'
import {
  changePassword,
  changePhone,
  getLoginHistory,
  refreshLoginHistory,
  updatePrivacySettings,
  setResumeVisibility,
  clearUserData,
  deleteAccount,
  getPrivacySettings
} from '@/api/auth'
import { getPersonalInfo } from '@/api/profile'

export default {
  name: 'AccountSettings',
  components: {
    SvgIcon
  },
  setup() {
    // 使用auth store获取用户信息
    const authStore = useAuthStore()

    const isEditing = ref(false)
    const saving = ref(false)
    const activeTab = ref('basic')

    // 模态框控制
    const showPasswordModal = ref(false)
    const showPhoneModal = ref(false)
    const showResumeVisibilityModal = ref(false)
    const isDeleteSectionVisible = ref(false)
    const showDataSharingPanel = ref(false)
    const showLoginHistoryPanel = ref(false)

    // 与模板兼容的变量
    const cancelReason = ref('')
    const confirmDelete = ref(false)

    // 用户账户信息 - 从store和API获取真实数据
    const accountInfo = reactive({
      username: '',
      email: '',
      phone: '',
      twoFactorEnabled: false,
      emailNotifications: true,
      smsNotifications: false,
      systemNotifications: true,
      marketingEmails: false,
      language: 'zh-CN',
      theme: 'light',
      timezone: 'Asia/Shanghai',
      lastPasswordChange: '2025-07-10' // 默认密码修改时间
    })
    
    // 隐私设置
    const privacySettings = reactive({
      dataSharing: true,
      resumeVisibility: 'limited'
    })
    
    // 表单数据
    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const phoneForm = reactive({
      newPhone: ''
    })
    
    // 登录历史
    const loginHistory = ref([])

    // 详细登录历史记录（从ResumeManagement迁移）
    const loginHistoryRecords = ref([
      {
        id: 1,
        loginTime: '2025-01-22 14:30:25',
        ipAddress: '192.168.1.100',
        location: '北京市',
        device: 'Windows - Chrome',
        status: 'success',
        statusText: '成功'
      },
      {
        id: 2,
        loginTime: '2025-01-22 09:15:42',
        ipAddress: '192.168.1.100',
        location: '北京市',
        device: 'Windows - Chrome',
        status: 'success',
        statusText: '成功'
      },
      {
        id: 3,
        loginTime: '2025-01-21 18:45:12',
        ipAddress: '192.168.1.100',
        location: '北京市',
        device: 'Windows - Chrome',
        status: 'success',
        statusText: '成功'
      },
      {
        id: 4,
        loginTime: '2025-01-21 10:22:33',
        ipAddress: '192.168.1.100',
        location: '北京市',
        device: 'Windows - Chrome',
        status: 'success',
        statusText: '成功'
      }
    ])

    // 简历可见性设置
    const resumeVisibility = ref('limited')

    // 当前时间
    const currentDateTime = ref(new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }))
    
    const errors = reactive({})
    const passwordStrength = ref(0)
    const showPassword = reactive({
      current: false,
      new: false,
      confirm: false
    })
    
    // 计算属性
    const lastPasswordChangeTime = computed(() => {
      return accountInfo.lastPasswordChange || '2025-07-10'
    })

    const maskedPhone = computed(() => {
      if (!accountInfo.phone) return '未绑定'
      return accountInfo.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    })
    
    const isFormValid = computed(() => {
      return Object.keys(errors).length === 0
    })
    
    // 工具方法
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString('zh-CN')
    }
    
    const validatePhone = (phone) => {
      const phoneRegex = /^1[3-9]\d{9}$/
      return phoneRegex.test(phone)
    }
    
    const validatePassword = (password) => {
      return password && password.length >= 6
    }
    
    // 模态框控制方法
    const openPasswordModal = () => {
      showPasswordModal.value = true
      // 清空表单和错误
      passwordForm.currentPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      Object.keys(errors).forEach(key => delete errors[key])
    }
    
    const closePasswordModal = () => {
      showPasswordModal.value = false
    }
    
    const openPhoneModal = () => {
      showPhoneModal.value = true
      phoneForm.newPhone = ''
      Object.keys(errors).forEach(key => delete errors[key])
    }
    
    const closePhoneModal = () => {
      showPhoneModal.value = false
    }
    
    const openResumeVisibilityModal = () => {
      showResumeVisibilityModal.value = true
      resumeVisibility.value = privacySettings.resumeVisibility
    }
    
    const closeResumeVisibilityModal = () => {
      showResumeVisibilityModal.value = false
    }

    const toggleDataSharingPanel = () => {
      showDataSharingPanel.value = !showDataSharingPanel.value
    }

    const updateCurrentTime = () => {
      currentDateTime.value = new Date().toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 切换登录历史面板
    const toggleLoginHistoryPanel = () => {
      showLoginHistoryPanel.value = !showLoginHistoryPanel.value
    }

    // 刷新登录历史记录
    const refreshLoginHistoryRecords = () => {
      // 这里可以调用API刷新登录历史
      console.log('刷新登录历史')
      alert('登录历史已刷新')
    }

    // 导出登录历史
    const exportLoginHistory = () => {
      // 这里可以调用API导出登录历史
      console.log('导出登录历史')
      alert('登录历史导出功能开发中')
    }

    // 密码修改功能
    const changePasswordHandler = async () => {
      // 验证表单
      if (!passwordForm.currentPassword) {
        errors.currentPassword = '请输入当前密码'
        return
      }
      if (!passwordForm.newPassword) {
        errors.newPassword = '请输入新密码'
        return
      }
      if (!passwordForm.confirmPassword) {
        errors.confirmPassword = '请确认新密码'
        return
      }
      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        errors.confirmPassword = '两次输入的密码不一致'
        return
      }
      if (!validatePassword(passwordForm.newPassword)) {
        errors.newPassword = '密码长度至少6个字符'
        return
      }
      
      saving.value = true
      
      try {
        await changePassword({
          current_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword
        })
        
        alert('密码修改成功')
        closePasswordModal()
        
      } catch (error) {
        console.error('密码修改失败:', error)
        errors.currentPassword = error.message || '密码修改失败，请检查当前密码是否正确'
      } finally {
        saving.value = false
      }
    }
    
    // 手机号更换功能
    const changePhoneHandler = async () => {
      if (!phoneForm.newPhone) {
        errors.newPhone = '请输入新手机号'
        return
      }
      if (!validatePhone(phoneForm.newPhone)) {
        errors.newPhone = '请输入正确的手机号格式'
        return
      }
      
      saving.value = true
      
      try {
        await changePhone({
          new_phone: phoneForm.newPhone
        })
        
        // 更新本地数据
        accountInfo.phone = phoneForm.newPhone
        alert('手机号更换成功')
        closePhoneModal()
        
      } catch (error) {
        console.error('手机号更换失败:', error)
        errors.newPhone = error.message || '手机号更换失败'
      } finally {
        saving.value = false
      }
    }
    
    // 获取登录历史
    const fetchLoginHistory = async () => {
      try {
        const response = await getLoginHistory()
        if (response.success) {
          loginHistory.value = response.data || []
        } else {
          throw new Error(response.message || '获取登录历史失败')
        }
      } catch (error) {
        console.error('获取登录历史失败:', error)
        // 使用模拟数据
        loginHistory.value = [
          {
            loginTime: Date.now() - 86400000,
            location: '上海市',
            deviceInfo: 'Windows Chrome',
            isAbnormal: false
          },
          {
            loginTime: Date.now() - 172800000,
            location: '北京市',
            deviceInfo: 'iPhone Safari',
            isAbnormal: true
          }
        ]
      }
    }
    
    const refreshLoginHistoryHandler = async () => {
      await fetchLoginHistory()
    }
    
    // 数据共享授权切换
    const toggleDataSharing = async () => {
      const newValue = !privacySettings.dataSharing
      
      try {
        const response = await updatePrivacySettings({
          data_sharing: newValue
        })
        
        if (response.success) {
          privacySettings.dataSharing = newValue
        } else {
          throw new Error(response.message || '设置保存失败')
        }
        
      } catch (error) {
        console.error('设置保存失败:', error)
        alert('设置保存失败，请重试')
      }
    }
    
    // 简历可见范围设置
    const saveResumeVisibility = async () => {
      saving.value = true
      
      try {
        const response = await setResumeVisibility({
          visibility: resumeVisibility.value
        })
        
        if (response.success) {
          privacySettings.resumeVisibility = resumeVisibility.value
          alert('简历可见范围设置已保存')
          closeResumeVisibilityModal()
        } else {
          throw new Error(response.message || '设置保存失败')
        }
        
      } catch (error) {
        console.error('设置保存失败:', error)
        alert('设置保存失败，请重试')
      } finally {
        saving.value = false
      }
    }
    
    // 清除用户痕迹
    const clearUserTraces = async () => {
      if (!confirm('确定要清除所有面试记录和评估历史吗？此操作不可恢复！')) {
        return
      }
      
      try {
        const response = await clearUserData(['all'])
        
        if (response.success) {
          alert('用户痕迹已清除')
        } else {
          throw new Error(response.message || '清除失败')
        }
        
      } catch (error) {
        console.error('清除失败:', error)
        alert('清除失败，请重试')
      }
    }
    
    // 账号注销
    const deleteAccountHandler = async () => {
      if (!confirm('确定要注销账号吗？此操作不可恢复！')) {
        return
      }
      
      try {
        const response = await deleteAccount({
          reason: cancelReason.value,
          confirm: confirmDelete.value
        })
        
        if (response.success) {
          alert('账号注销成功')
          // 跳转到登录页面
          window.location.href = '/login'
        } else {
          throw new Error(response.message || '账号注销失败')
        }
        
      } catch (error) {
        console.error('账号注销失败:', error)
        alert('账号注销失败，请重试')
      }
    }
    
    // 获取用户数据
    const fetchUserData = async () => {
      try {
        // 从auth store获取基本用户信息
        if (authStore.user) {
          accountInfo.username = authStore.user.username || ''
          accountInfo.email = authStore.user.email || ''
        }

        // 尝试获取详细个人信息（如果后端可用）
        try {
          const personalInfoResponse = await getPersonalInfo()
          if (personalInfoResponse.success && personalInfoResponse.data) {
            const personalInfo = personalInfoResponse.data
            accountInfo.phone = personalInfo.phone || ''
            accountInfo.email = personalInfo.email || accountInfo.email
          }
        } catch (apiError) {
          console.warn('个人信息API不可用，使用默认数据')
        }

        // 尝试获取隐私设置（如果后端可用）
        try {
          const privacyResponse = await getPrivacySettings()
          if (privacyResponse.success && privacyResponse.data) {
            const settings = privacyResponse.data
            privacySettings.dataSharing = settings.data_sharing || false
            privacySettings.resumeVisibility = settings.resume_visibility || 'limited'
          }
        } catch (apiError) {
          console.warn('隐私设置API不可用，使用默认数据')
        }

      } catch (error) {
        console.error('获取用户数据失败:', error)
      } finally {
        // 确保有基本的用户数据显示
        if (!accountInfo.username && authStore.user) {
          accountInfo.username = authStore.user.username || '用户'
          accountInfo.email = authStore.user.email || 'user@example.com'
        }
        if (!accountInfo.phone) {
          accountInfo.phone = '13800138000' // 默认手机号
        }
      }
    }

    // 定时更新时间
    const timeInterval = setInterval(updateCurrentTime, 60000) // 每分钟更新一次

    // 组件挂载时获取数据
    onMounted(() => {
      fetchUserData()
      fetchLoginHistory()
    })

    // 组件卸载时清理定时器
    onUnmounted(() => {
      clearInterval(timeInterval)
    })
    
    return {
      // 与模板兼容的变量
      cancelReason,
      confirmDelete,
      
      // 新增的功能变量
      isEditing,
      saving,
      activeTab,
      accountInfo,
      privacySettings,
      passwordForm,
      phoneForm,
      loginHistory,
      resumeVisibility,
      errors,
      passwordStrength,
      showPassword,
      showPasswordModal,
      showPhoneModal,
      showResumeVisibilityModal,
      isDeleteSectionVisible,
      showDataSharingPanel,
      showLoginHistoryPanel,
      loginHistoryRecords,
      currentDateTime,

      // 计算属性
      lastPasswordChangeTime,
      maskedPhone,
      isFormValid,

      // 方法
      formatTime,
      updateCurrentTime,
      toggleDataSharingPanel,
      toggleLoginHistoryPanel,
      refreshLoginHistoryRecords,
      exportLoginHistory,
      fetchUserData,
      openPasswordModal,
      closePasswordModal,
      openPhoneModal,
      closePhoneModal,
      openResumeVisibilityModal,
      closeResumeVisibilityModal,
      changePassword: changePasswordHandler,
      changePhone: changePhoneHandler,
      refreshLoginHistory: refreshLoginHistoryHandler,
      toggleDataSharing,
      saveResumeVisibility,
      clearUserTraces,
      deleteAccount: deleteAccountHandler
    }
  }
}
</script>

<style scoped>
.account-settings {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: #6b7280;
}

.breadcrumb-item {
  color: #6b7280;
}

.breadcrumb-item.current {
  color: #722ED1;
  font-weight: 500;
}

.breadcrumb-separator {
  margin: 0 8px;
  color: #9ca3af;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 32px;
}

.settings-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid #f3f4f6;
}

.item-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.item-icon {
  width: 20px;
  height: 20px;
  margin-right: 16px;
  color: #6b7280;
}

.item-content {
  flex: 1;
}

.item-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.item-desc {
  font-size: 14px;
  color: #6b7280;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.action-btn.secondary {
  background: #f9fafb;
  color: #722ED1;
  border: 1px solid #e5e7eb;
}

.action-btn.secondary:hover {
  background: #f3f4f6;
}

.action-btn.danger {
  background: #ef4444;
  color: white;
}

.action-btn.danger:hover {
  background: #dc2626;
}

.action-btn:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background: #d1d5db;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle-switch.active {
  background: #722ED1;
}

.toggle-slider {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
}

.toggle-switch.active .toggle-slider {
  transform: translateX(20px);
}

.login-history {
  margin-left: 36px;
  margin-top: 16px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.history-info {
  display: flex;
  gap: 16px;
}

.history-time {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.history-location {
  font-size: 14px;
  color: #6b7280;
}

.history-device {
  font-size: 14px;
  color: #6b7280;
}

.warning-tag {
  background: #fef2f2;
  color: #ef4444;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.warning-notice {
  display: flex;
  align-items: center;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.warning-icon {
  margin-right: 12px;
  font-size: 18px;
}

.warning-text {
  color: #dc2626;
  font-weight: 500;
}

.data-list {
  list-style: none;
  padding: 0;
  margin: 0 0 24px 0;
}

.data-list li {
  padding: 8px 0;
  padding-left: 30px;
  position: relative;
  color: #6b7280;
  font-size: 14px;
}

.data-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #ef4444;
  font-weight: bold;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-select {
  width: 100%;
  max-width: 300px;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
  background: white;
}

.form-select:focus {
  outline: none;
  border-color: #722ED1;
  box-shadow: 0 0 0 3px rgba(114, 45, 209, 0.1);
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.checkbox-container input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 3px;
  margin-right: 12px;
  position: relative;
  transition: all 0.2s;
}

.checkbox-container input[type="checkbox"]:checked + .checkmark {
  background: #722ED1;
  border-color: #722ED1;
}

.checkbox-container input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  color: white;
  font-size: 12px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 账号注销区域样式 - 设计得更小更低调 */
.delete-section {
  margin-top: 32px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.delete-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.delete-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 0;
}

.collapse-indicator {
  font-size: 12px;
  font-weight: 400;
  color: #9ca3af;
}

.delete-content {
  margin-top: 12px;
}

.delete-warning {
  padding: 12px;
  margin-bottom: 12px;
  border-radius: 6px;
}

.delete-warning .warning-icon {
  font-size: 14px;
}

.delete-warning .warning-text {
  font-size: 12px;
}

.delete-data-list {
  margin-bottom: 16px;
}

.delete-data-list li {
  font-size: 12px;
  padding-top: 4px;
  padding-bottom: 4px;
}

.delete-form-group {
  margin-bottom: 12px;
}

.delete-form-label {
  font-size: 12px;
  margin-bottom: 4px;
}

.delete-form-select {
  max-width: 250px;
  font-size: 12px;
  padding: 8px;
}

.delete-checkbox {
  font-size: 12px;
}

.delete-btn {
  font-size: 12px;
  padding: 6px 12px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #722ED1;
  box-shadow: 0 0 0 3px rgba(114, 46, 209, 0.1);
}

.form-input.error {
  border-color: #ef4444;
}

.error-text {
  display: block;
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

.action-btn.primary {
  background: #722ED1;
  color: white;
  border: none;
}

.action-btn.primary:hover {
  background: #5A1F9F;
}

.action-btn.primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

/* 简历可见范围设置样式 */
.visibility-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.radio-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-option:hover {
  border-color: #722ED1;
  background: #f9fafb;
}

.radio-option input[type="radio"] {
  margin: 0;
  accent-color: #722ED1;
}

.radio-option input[type="radio"]:checked + .radio-label {
  color: #722ED1;
  font-weight: 600;
}

.radio-label {
  font-size: 16px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 4px;
}

.radio-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

/* 无历史记录样式 */
.no-history {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.no-history p {
  margin: 0;
  font-size: 14px;
}

/* 登录历史面板样式 - 从ResumeManagement迁移 */
.data-sharing-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.data-sharing-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.data-sharing-btn.active {
  background: #ddd6fe;
  border-color: #8b5cf6;
  color: #7c3aed;
}

.data-sharing-btn .chevron {
  width: 16px;
  height: 16px;
  transition: transform 0.2s ease;
}

.data-sharing-btn.active .chevron {
  transform: rotate(180deg);
}

/* 登录历史面板 */
.login-history-panel {
  margin-top: 16px;
  margin-left: 36px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.history-content {
  padding: 20px;
}

.history-header {
  margin-bottom: 20px;
}

.history-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.history-header p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.history-item-detailed {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.history-item-detailed:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.history-info-detailed {
  flex: 1;
}

.history-time-detailed {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
  font-family: 'Courier New', monospace;
}

.history-details {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #6b7280;
}

.history-ip {
  font-family: 'Courier New', monospace;
}

.history-location::before {
  content: '📍';
  margin-right: 4px;
}

.history-device::before {
  content: '💻';
  margin-right: 4px;
}

.history-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
}

.history-status.success {
  color: #059669;
}

.history-status.failed {
  color: #dc2626;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.history-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary {
  padding: 8px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-primary {
  padding: 8px 16px;
  background: #8b5cf6;
  border: 1px solid #8b5cf6;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #7c3aed;
  border-color: #7c3aed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 16px;
  }
  
  .visibility-options {
    gap: 12px;
  }
  
  .radio-option {
    padding: 12px;
  }

  .login-history-panel {
    margin-left: 0;
  }

  .history-details {
    flex-direction: column;
    gap: 4px;
  }

  .history-actions {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
