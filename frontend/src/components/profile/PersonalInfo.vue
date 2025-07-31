<template>
  <div class="personal-info">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item">个人中心</span>
      <span class="breadcrumb-divider">></span>
      <span class="breadcrumb-item active">个人信息</span>
    </div>

    <!-- 基础信息 -->
    <div class="info-section">
      <div class="section-header">
        <h2 class="section-title">基础信息</h2>
        <button class="edit-btn" @click="toggleEdit">{{ isEditing ? '取消' : '编辑' }}</button>
      </div>

      <div class="info-content">
        <!-- 基础信息水平布局 -->
        <div class="basic-info-layout">
          <!-- 左侧头像区域 -->
          <div class="avatar-section">
            <div class="avatar-upload" @click="uploadAvatarFile">
              <div class="avatar-placeholder" v-if="!userInfo.avatar">
                <SvgIcon name="frame" />
              </div>
              <img v-else :src="userInfo.avatar" alt="头像" class="avatar-img" />
            </div>
            <p class="avatar-tip">点击更换头像</p>
            <div v-if="errors.avatar" class="error-message">{{ errors.avatar }}</div>
          </div>

          <!-- 右侧表单区域 -->
          <div class="form-section">
            <div class="form-grid">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">用户名<span class="required">*</span></label>
                  <input 
                    type="text" 
                    class="form-input" 
                    :class="{ 'error': errors.name }"
                    placeholder="请输入用户名"
                    v-model="userInfo.name"
                    :disabled="!isEditing"
                    @blur="validateField('name')"
                  />
                  <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
                </div>
                <div class="form-group">
                  <label class="form-label">性别<span class="required">*</span></label>
                  <select 
                    class="form-select" 
                    :class="{ 'error': errors.gender }"
                    v-model="userInfo.gender"
                    :disabled="!isEditing"
                    @change="validateField('gender')"
                  >
                    <option value="">请选择</option>
                    <option value="male">男</option>
                    <option value="female">女</option>
                  </select>
                  <div v-if="errors.gender" class="error-message">{{ errors.gender }}</div>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">出生年月</label>
                  <input 
                    type="date" 
                    class="form-input date-input" 
                    :class="{ 'error': errors.birthDate }"
                    v-model="userInfo.birthDate"
                    :disabled="!isEditing"
                    :max="maxBirthDate"
                    @change="validateField('birthDate')"
                  />
                  <div v-if="errors.birthDate" class="error-message">{{ errors.birthDate }}</div>
                </div>
                <div class="form-group">
                  <label class="form-label">联系电话<span class="required">*</span></label>
                  <input 
                    type="tel" 
                    class="form-input" 
                    :class="{ 'error': errors.phone }"
                    placeholder="请输入手机号码"
                    v-model="userInfo.phone"
                    :disabled="!isEditing"
                    @blur="validateField('phone')"
                  />
                  <div v-if="errors.phone" class="error-message">{{ errors.phone }}</div>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">邮箱<span class="required">*</span></label>
                  <input 
                    type="email" 
                    class="form-input" 
                    :class="{ 'error': errors.email }"
                    placeholder="请输入邮箱地址"
                    v-model="userInfo.email"
                    :disabled="!isEditing"
                    @blur="validateField('email')"
                  />
                  <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
                </div>
                <div class="form-group">
                  <label class="form-label">微信</label>
                  <input 
                    type="text" 
                    class="form-input" 
                    placeholder="请输入微信号"
                    v-model="userInfo.contact"
                    :disabled="!isEditing"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  
    <!-- 教育背景 -->
    <div class="info-section">
      <div class="section-header">
        <h2 class="section-title">教育背景</h2>
        <button class="edit-btn" @click="toggleEdit">{{ isEditing ? '取消' : '编辑' }}</button>
      </div>

      <div class="info-content">
        <div class="form-grid">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">学校<span class="required">*</span></label>
              <div class="autocomplete-wrapper">
                <input 
                  type="text" 
                  class="form-input" 
                  :class="{ 'error': errors.school }"
                  :placeholder="schoolsLoading ? '正在加载学校数据...' : '请输入学校名称进行搜索'"
                  v-model="userInfo.education.school"
                  :disabled="!isEditing"
                  @input="handleSchoolInput"
                  @blur="validateField('school')"
                />
                <div v-if="schoolSuggestions.length > 0 && isEditing && showSchoolSuggestions" class="suggestions-dropdown">
                  <div 
                    v-for="school in schoolSuggestions" 
                    :key="school.id"
                    class="suggestion-item"
                    @click="selectSchool(school)"
                  >
                    <div class="school-info">
                      <div class="school-name">{{ school.name }}</div>
                      <div class="school-detail">{{ school.province }} {{ school.city }} - {{ school.type }}</div>
                    </div>
                  </div>
                  <div v-if="schoolSuggestions.length >= 10" class="suggestion-more">
                    显示前10个结果，请输入更多关键词缩小范围
                  </div>
                </div>
                <div v-if="schoolsLoading && isEditing" class="loading-indicator">
                  <div class="loading-text">正在搜索全国高校...</div>
                </div>
              </div>
              <div v-if="errors.school" class="error-message">{{ errors.school }}</div>
            </div>
            <div class="form-group">
              <label class="form-label">学院<span class="required">*</span></label>
              <div class="autocomplete-wrapper">
                <input 
                  type="text" 
                  class="form-input" 
                  :class="{ 'error': errors.college }"
                  :placeholder="userInfo.education.school ? '请输入学院名称进行搜索' : '请先选择学校'"
                  v-model="userInfo.education.college"
                  :disabled="!isEditing || !selectedSchool"
                  @input="handleCollegeInput"
                  @blur="validateField('college')"
                />
                <div v-if="collegeSuggestions.length > 0 && isEditing && showCollegeSuggestions" class="suggestions-dropdown">
                  <div 
                    v-for="college in collegeSuggestions" 
                    :key="college.id"
                    class="suggestion-item"
                    @click="selectCollege(college)"
                  >
                    <div class="college-info">
                      <div class="college-name">{{ college.name }}</div>
                      <div class="college-detail">{{ college.description || '点击选择此学院' }}</div>
                    </div>
                  </div>
                </div>
                <div v-if="collegeLoading && isEditing" class="loading-indicator">
                  <div class="loading-text">正在搜索学院信息...</div>
                </div>
              </div>
              <div v-if="errors.college" class="error-message">{{ errors.college }}</div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">专业<span class="required">*</span></label>
              <div class="autocomplete-wrapper">
                <input 
                  type="text" 
                  class="form-input" 
                  :class="{ 'error': errors.major }"
                  :placeholder="userInfo.education.college ? '请输入专业名称进行搜索' : '请先选择学院'"
                  v-model="userInfo.education.major"
                  :disabled="!isEditing || !selectedCollege"
                  @input="handleMajorInput"
                  @blur="validateField('major')"
                />
                <div v-if="majorSuggestions.length > 0 && isEditing && showMajorSuggestions" class="suggestions-dropdown">
                  <div 
                    v-for="major in majorSuggestions" 
                    :key="major.id"
                    class="suggestion-item"
                    @click="selectMajor(major)"
                  >
                    <div class="major-info">
                      <div class="major-name">{{ major.name }}</div>
                      <div class="major-detail">{{ major.code ? `专业代码: ${major.code}` : major.category }}</div>
                    </div>
                  </div>
                </div>
                <div v-if="majorLoading && isEditing" class="loading-indicator">
                  <div class="loading-text">正在搜索专业信息...</div>
                </div>
              </div>
              <div v-if="errors.major" class="error-message">{{ errors.major }}</div>
            </div>
            <div class="form-group">
              <label class="form-label">学历<span class="required">*</span></label>
              <select 
                class="form-select" 
                :class="{ 'error': errors.degree }"
                v-model="userInfo.education.degree"
                :disabled="!isEditing"
                @change="handleDegreeChange"
              >
                <option value="">请选择</option>
                <option value="associate">大专</option>
                <option value="bachelor">本科</option>
                <option value="master">硕士</option>
                <option value="doctor">博士</option>
              </select>
              <div v-if="errors.degree" class="error-message">{{ errors.degree }}</div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">入学-毕业时间<span class="required">*</span></label>
              <div class="date-range">
                <input 
                  type="date" 
                  class="form-input date-input" 
                  v-model="userInfo.education.startDate"
                  :disabled="!isEditing"
                  @change="calculateEndDate"
                />
                <span class="date-separator">至</span>
                <input 
                  type="date" 
                  class="form-input date-input" 
                  v-model="userInfo.education.endDate"
                  :disabled="!isEditing"
                />
              </div>
              <div v-if="errors.startDate || errors.endDate" class="error-message">
                {{ errors.startDate || errors.endDate }}
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">GPA/排名</label>
              <input 
                type="text" 
                class="form-input" 
                :class="{ 'error': errors.gpa }"
                placeholder="请输入GPA或排名"
                v-model="userInfo.education.gpa"
                :disabled="!isEditing"
                @blur="validateField('gpa')"
              />
              <div v-if="errors.gpa" class="error-message">{{ errors.gpa }}</div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label class="form-label">主修课程</label>
              <textarea 
                class="form-textarea" 
                placeholder="请输入主修课程，用逗号分隔"
                v-model="userInfo.education.courses"
                :disabled="!isEditing"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息提示区域 -->
    <div v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </div>
    <div v-if="errorMessage" class="message error-message">
      {{ errorMessage }}
    </div>

    <!-- 保存按钮 -->
    <div class="save-section">
      <button 
        class="save-btn" 
        @click="saveChanges" 
        :disabled="!isEditing || saving"
        :class="{ 'active': isEditing && !saving }"
      >
        {{ saving ? '保存中...' : '保存修改' }}
      </button>
    </div>

    <!-- 隐藏的文件输入 -->
    <input 
      ref="fileInput" 
      type="file" 
      accept="image/png,image/jpg,image/jpeg,image/gif" 
      style="display: none"
      @change="handleAvatarUpload"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import SvgIcon from '@/components/common/SvgIcon.vue'
import { useAuthStore } from '@/stores/auth'
import {
  getPersonalInfo,
  updatePersonalInfo,
  getEducationInfo,
  updateEducationInfo,
  getSkills,
  updateSkills,
  uploadAvatar as uploadAvatarAPI,
  getProfileSummary
} from '@/api/profile'

export default {
  name: 'PersonalInfo',
  components: {
    SvgIcon
  },
  setup() {
    const authStore = useAuthStore()
    const isEditing = ref(false)
    const saving = ref(false)
    const loading = ref(false)
    const fileInput = ref(null)
    const successMessage = ref('')
    const errorMessage = ref('')
    
    const userInfo = reactive({
      avatar: '',
      name: '',
      gender: '',
      birthDate: '',
      phone: '',
      email: '',
      contact: '',
      education: {
        school: '',
        college: '',
        major: '',
        degree: '',
        startDate: '',
        endDate: '',
        gpa: '',
        courses: ''
      }
    })
    
    const errors = reactive({})
    
    // 学校相关
    const schoolSuggestions = ref([])
    const schoolsLoading = ref(false)
    const showSchoolSuggestions = ref(false)
    const selectedSchool = ref(null)
    
    // 学院相关
    const collegeSuggestions = ref([])
    const collegeLoading = ref(false)
    const showCollegeSuggestions = ref(false)
    const selectedCollege = ref(null)
    
    // 专业相关
    const majorSuggestions = ref([])
    const majorLoading = ref(false)
    const showMajorSuggestions = ref(false)
    const selectedMajor = ref(null)
    
    // 防抖定时器
    let schoolSearchTimer = null
    let collegeSearchTimer = null
    let majorSearchTimer = null
    
    // 学历年限映射
    const degreeYears = {
      associate: 3, // 大专3年
      bachelor: 4,  // 本科4年
      master: 3,    // 硕士3年
      doctor: 2     // 博士2年
    }

    // 加载个人信息
    const loadPersonalInfo = async () => {
      try {
        loading.value = true
        const response = await getPersonalInfo()
        
        if (response.success) {
          const data = response.data
          userInfo.avatar = data.avatar || authStore.userAvatar || ''
          userInfo.name = data.name || authStore.userName || ''
          userInfo.gender = data.gender || ''
          userInfo.birthDate = data.birth_date || ''
          userInfo.phone = data.phone || ''
          userInfo.email = data.email || authStore.userEmail || ''
          userInfo.contact = data.contact || ''
        } else {
          // 如果没有个人信息数据，使用auth store中的数据
          userInfo.name = authStore.userName || ''
          userInfo.email = authStore.userEmail || ''
          userInfo.avatar = authStore.userAvatar || ''
        }
      } catch (error) {
        console.error('加载个人信息失败:', error)
        // 出错时也使用auth store中的数据
        userInfo.name = authStore.userName || ''
        userInfo.email = authStore.userEmail || ''
        userInfo.avatar = authStore.userAvatar || ''
      } finally {
        loading.value = false
      }
    }

    // 加载教育背景
    const loadEducationInfo = async () => {
      try {
        const response = await getEducationInfo()
        
        if (response.success) {
          const data = response.data
          userInfo.education.school = data.school || ''
          userInfo.education.college = data.college || ''
          userInfo.education.major = data.major || ''
          userInfo.education.degree = data.degree || ''
          userInfo.education.startDate = data.start_date || ''
          userInfo.education.endDate = data.end_date || ''
          userInfo.education.gpa = data.gpa || ''
          userInfo.education.courses = data.courses || ''
        }
      } catch (error) {
        console.error('加载教育背景失败:', error)
      }
    }

    // 组件挂载时加载数据
    onMounted(() => {
      loadPersonalInfo()
      loadEducationInfo()
    })

    // 计算毕业时间
    const calculateEndDate = () => {
      if (userInfo.education.startDate && userInfo.education.degree) {
        const startDate = new Date(userInfo.education.startDate)
        const years = degreeYears[userInfo.education.degree]
        if (years) {
          const endDate = new Date(startDate)
          endDate.setFullYear(startDate.getFullYear() + years)
          userInfo.education.endDate = endDate.toISOString().split('T')[0]
        }
      }
    }

    // 处理学历变化
    const handleDegreeChange = () => {
      validateField('degree')
      calculateEndDate()
    }

    // 监听入学时间变化
    watch(() => userInfo.education.startDate, (newVal) => {
      if (newVal) {
        calculateEndDate()
      }
    })

    // 计算属性
    const maxBirthDate = computed(() => {
      const today = new Date()
      const maxDate = new Date(today.getFullYear() - 16, today.getMonth(), today.getDate())
      return maxDate.toISOString().split('T')[0]
    })
    
    const maxDate = computed(() => {
      return new Date().toISOString().split('T')[0]
    })
    
    const isFormValid = computed(() => {
      return Object.keys(errors).length === 0 && 
             userInfo.name && 
             userInfo.gender && 
             userInfo.phone && 
             userInfo.email &&
             userInfo.education.school &&
             userInfo.education.college &&
             userInfo.education.major &&
             userInfo.education.degree
    })
    
    // 验证方法
    const validateEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    }
    
    const validatePhone = (phone) => {
      const phoneRegex = /^1[3-9]\d{9}$/
      return phoneRegex.test(phone)
    }
    
    const validateGPA = (gpa) => {
      if (!gpa) return true // 可选字段
      // 只要包含斜杠就认为是排名格式，或者是0-4之间的GPA
      return gpa.includes('/') || /^[0-4](\.\d{1,2})?$/.test(gpa)
    }
    
    const validateField = (field) => {
      delete errors[field]
      
      switch (field) {
        case 'name':
          if (!userInfo.name) {
            errors.name = '姓名不能为空'
          } else if (userInfo.name.length < 2) {
            errors.name = '姓名至少2个字符'
          } else if (userInfo.name.length > 20) {
            errors.name = '姓名不能超过20个字符'
          }
          break
          
        case 'gender':
          if (!userInfo.gender) {
            errors.gender = '请选择性别'
          }
          break
          
        case 'birthDate':
          if (userInfo.birthDate) {
            const birthYear = new Date(userInfo.birthDate).getFullYear()
            const currentYear = new Date().getFullYear()
            if (currentYear - birthYear < 16) {
              errors.birthDate = '年龄不能小于16岁'
            } else if (currentYear - birthYear > 100) {
              errors.birthDate = '请输入有效的出生年月'
            }
          }
          break
          
        case 'phone':
          if (!userInfo.phone) {
            errors.phone = '联系电话不能为空'
          } else if (!validatePhone(userInfo.phone)) {
            errors.phone = '请输入正确的手机号码'
          }
          break
          
        case 'email':
          if (!userInfo.email) {
            errors.email = '邮箱不能为空'
          } else if (!validateEmail(userInfo.email)) {
            errors.email = '请输入正确的邮箱格式'
          }
          break
          
        case 'school':
          if (!userInfo.education.school) {
            errors.school = '学校不能为空'
          }
          break
          
        case 'college':
          if (!userInfo.education.college) {
            errors.college = '学院不能为空'
          }
          break
          
        case 'major':
          if (!userInfo.education.major) {
            errors.major = '专业不能为空'
          }
          break
          
        case 'degree':
          if (!userInfo.education.degree) {
            errors.degree = '请选择学历'
          }
          break
          
        case 'gpa':
          if (userInfo.education.gpa && !validateGPA(userInfo.education.gpa)) {
            errors.gpa = '请输入正确的GPA格式（如：3.8 或 排名5/100）'
          }
          break
      }
    }
    
    const validateAllFields = () => {
      const fields = ['name', 'gender', 'phone', 'email', 'school', 'college', 'major', 'degree', 'birthDate', 'gpa']
      fields.forEach(field => validateField(field))
    }
    
    // 教育数据API服务
    const EducationAPI = {
      // 搜索学校
      async searchSchools(keyword) {
        if (!keyword || keyword.length < 2) return []
        
        try {
          // 模拟多个数据源
          const apis = [
            {
              url: `https://api.hcfpz.cn/un/schools`,
              transform: (data) => {
                if (Array.isArray(data)) {
                  return data
                    .filter(item => {
                      const name = item.school || item.name || item.学校名称 || ''
                      return name.includes(keyword)
                    })
                    .map((item, index) => ({
                      id: index + 1,
                      name: item.school || item.name || item.学校名称,
                      province: item.province || item.省份 || '未知',
                      city: item.city || item.城市 || '未知',
                      type: item.type || '普通高校'
                    }))
                    .slice(0, 10)
                }
                return []
              }
            }
          ]

          for (const api of apis) {
            try {
              const response = await fetch(api.url)
              if (response.ok) {
                const data = await response.json()
                const results = api.transform(data)
                if (results.length > 0) return results
              }
            } catch (error) {
              console.warn(`学校API ${api.url} 失败:`, error.message)
            }
          }

          // 备用本地数据
          return this.getLocalSchools(keyword)
        } catch (error) {
          console.error('搜索学校失败:', error)
          return this.getLocalSchools(keyword)
        }
      },

      // 本地学校数据备选
      getLocalSchools(keyword) {
        const schools = [
          { name: '清华大学', province: '北京市', city: '北京市', type: '985高校' },
          { name: '北京大学', province: '北京市', city: '北京市', type: '985高校' },
          { name: '复旦大学', province: '上海市', city: '上海市', type: '985高校' },
          { name: '上海交通大学', province: '上海市', city: '上海市', type: '985高校' },
          { name: '浙江大学', province: '浙江省', city: '杭州市', type: '985高校' },
          { name: '中国科学技术大学', province: '安徽省', city: '合肥市', type: '985高校' },
          { name: '南京大学', province: '江苏省', city: '南京市', type: '985高校' },
          { name: '华中科技大学', province: '湖北省', city: '武汉市', type: '985高校' },
          { name: '中山大学', province: '广东省', city: '广州市', type: '985高校' },
          { name: '西安交通大学', province: '陕西省', city: '西安市', type: '985高校' },
          { name: '哈尔滨工业大学', province: '黑龙江省', city: '哈尔滨市', type: '985高校' },
          { name: '北京航空航天大学', province: '北京市', city: '北京市', type: '985高校' },
          { name: '北京理工大学', province: '北京市', city: '北京市', type: '985高校' },
          { name: '同济大学', province: '上海市', city: '上海市', type: '985高校' },
          { name: '东南大学', province: '江苏省', city: '南京市', type: '985高校' },
          { name: '天津大学', province: '天津市', city: '天津市', type: '985高校' },
          { name: '华南理工大学', province: '广东省', city: '广州市', type: '985高校' },
          { name: '山东大学', province: '山东省', city: '济南市', type: '985高校' },
          { name: '四川大学', province: '四川省', city: '成都市', type: '985高校' },
          { name: '吉林大学', province: '吉林省', city: '长春市', type: '985高校' },
          { name: '厦门大学', province: '福建省', city: '厦门市', type: '985高校' },
          { name: '湖南大学', province: '湖南省', city: '长沙市', type: '985高校' }
        ]
        
        return schools
          .filter(school => school.name.includes(keyword))
          .map((school, index) => ({ id: index + 1, ...school }))
          .slice(0, 10)
      },

      // 搜索学院
      async searchColleges(schoolName, keyword) {
        if (!schoolName || !keyword || keyword.length < 1) return []
        
        // 根据学校类型返回不同的学院
        const collegeMap = {
          '清华大学': [
            { name: '计算机科学与技术系', description: '计算机学院' },
            { name: '电子工程系', description: '电子信息与通信工程学院' },
            { name: '自动化系', description: '自动化与工业工程学院' },
            { name: '软件学院', description: '软件工程' },
            { name: '数学系', description: '理学院' },
            { name: '物理系', description: '理学院' },
            { name: '化学系', description: '理学院' },
            { name: '生命科学学院', description: '生命科学与医学部' },
            { name: '经济管理学院', description: '经管学部' },
            { name: '法学院', description: '文科学部' }
          ],
          '北京大学': [
            { name: '信息科学技术学院', description: '信息技术' },
            { name: '工学院', description: '工程技术' },
            { name: '数学科学学院', description: '理学部' },
            { name: '物理学院', description: '理学部' },
            { name: '化学与分子工程学院', description: '理学部' },
            { name: '生命科学学院', description: '理学部' },
            { name: '光华管理学院', description: '经济管理' },
            { name: '法学院', description: '社会科学部' },
            { name: '新闻与传播学院', description: '社会科学部' },
            { name: '外国语学院', description: '人文学部' }
          ]
        }
        
        // 通用学院模板
        const defaultColleges = [
          { name: '计算机学院', description: '计算机科学与技术' },
          { name: '软件学院', description: '软件工程' },
          { name: '信息学院', description: '信息技术' },
          { name: '机械学院', description: '机械工程' },
          { name: '电气学院', description: '电气工程' },
          { name: '经济学院', description: '经济管理' },
          { name: '管理学院', description: '工商管理' },
          { name: '文学院', description: '中文外语' },
          { name: '理学院', description: '数理化生' },
          { name: '法学院', description: '法律政治' }
        ]
        
        const colleges = collegeMap[schoolName] || defaultColleges
        
        return colleges
          .filter(college => college.name.includes(keyword))
          .map((college, index) => ({ id: index + 1, ...college }))
          .slice(0, 8)
      },

      // 搜索专业
      async searchMajors(collegeName, keyword) {
        if (!collegeName || !keyword || keyword.length < 1) return []
        
        // 根据学院返回相关专业
        const majorMap = {
          '计算机': [
            { name: '计算机科学与技术', code: '080901', category: '工学' },
            { name: '软件工程', code: '080902', category: '工学' },
            { name: '网络工程', code: '080903', category: '工学' },
            { name: '信息安全', code: '080904K', category: '工学' },
            { name: '物联网工程', code: '080905', category: '工学' },
            { name: '数字媒体技术', code: '080906', category: '工学' },
            { name: '智能科学与技术', code: '080907T', category: '工学' },
            { name: '空间信息与数字技术', code: '080908T', category: '工学' },
            { name: '电子与计算机工程', code: '080909T', category: '工学' },
            { name: '数据科学与大数据技术', code: '080910T', category: '工学' }
          ],
          '软件': [
            { name: '软件工程', code: '080902', category: '工学' },
            { name: '数字媒体技术', code: '080906', category: '工学' },
            { name: '网络工程', code: '080903', category: '工学' },
            { name: '信息安全', code: '080904K', category: '工学' }
          ],
          '经济': [
            { name: '经济学', code: '020101', category: '经济学' },
            { name: '经济统计学', code: '020102', category: '经济学' },
            { name: '国民经济管理', code: '020103T', category: '经济学' },
            { name: '资源与环境经济学', code: '020104T', category: '经济学' },
            { name: '商务经济学', code: '020105T', category: '经济学' },
            { name: '能源经济', code: '020106T', category: '经济学' },
            { name: '金融学', code: '020301K', category: '经济学' },
            { name: '金融工程', code: '020302', category: '经济学' },
            { name: '保险学', code: '020303', category: '经济学' },
            { name: '投资学', code: '020304', category: '经济学' }
          ],
          '管理': [
            { name: '工商管理', code: '120201K', category: '管理学' },
            { name: '市场营销', code: '120202', category: '管理学' },
            { name: '会计学', code: '120203K', category: '管理学' },
            { name: '财务管理', code: '120204', category: '管理学' },
            { name: '国际商务', code: '120205', category: '管理学' },
            { name: '人力资源管理', code: '120206', category: '管理学' },
            { name: '审计学', code: '120207', category: '管理学' },
            { name: '资产评估', code: '120208', category: '管理学' },
            { name: '物业管理', code: '120209', category: '管理学' },
            { name: '文化产业管理', code: '120210', category: '管理学' }
          ],
          '机械': [
            { name: '机械工程', code: '080201', category: '工学' },
            { name: '机械设计制造及其自动化', code: '080202', category: '工学' },
            { name: '材料成型及控制工程', code: '080203', category: '工学' },
            { name: '机械电子工程', code: '080204', category: '工学' },
            { name: '工业设计', code: '080205', category: '工学' },
            { name: '过程装备与控制工程', code: '080206', category: '工学' },
            { name: '车辆工程', code: '080207', category: '工学' },
            { name: '汽车服务工程', code: '080208', category: '工学' }
          ]
        }
        
        // 查找匹配的专业分类
        let matchedMajors = []
        for (const [key, majors] of Object.entries(majorMap)) {
          if (collegeName.includes(key)) {
            matchedMajors = [...matchedMajors, ...majors]
          }
        }
        
        // 如果没有匹配的，返回通用专业
        if (matchedMajors.length === 0) {
          matchedMajors = [
            { name: '计算机科学与技术', code: '080901', category: '工学' },
            { name: '软件工程', code: '080902', category: '工学' },
            { name: '电子信息工程', code: '080701', category: '工学' },
            { name: '通信工程', code: '080703', category: '工学' },
            { name: '自动化', code: '080801', category: '工学' },
            { name: '机械工程', code: '080201', category: '工学' },
            { name: '电气工程及其自动化', code: '080601', category: '工学' },
            { name: '土木工程', code: '081001', category: '工学' },
            { name: '化学工程与工艺', code: '081301', category: '工学' },
            { name: '经济学', code: '020101', category: '经济学' }
          ]
        }
        
        return matchedMajors
          .filter(major => major.name.includes(keyword))
          .map((major, index) => ({ id: index + 1, ...major }))
          .slice(0, 8)
      }
    }

    // 学校搜索处理
    const handleSchoolInput = (event) => {
      const keyword = event.target.value.trim()
      
      // 清除之前的定时器
      if (schoolSearchTimer) {
        clearTimeout(schoolSearchTimer)
      }
      
      if (keyword.length < 2) {
        schoolSuggestions.value = []
        showSchoolSuggestions.value = false
        return
      }
      
      // 防抖搜索
      schoolSearchTimer = setTimeout(async () => {
        try {
          schoolsLoading.value = true
          showSchoolSuggestions.value = true
          
          const results = await EducationAPI.searchSchools(keyword)
          schoolSuggestions.value = results
          console.log(`找到 ${results.length} 所学校:`, results.slice(0, 3))
          
        } catch (error) {
          console.error('学校搜索失败:', error)
          schoolSuggestions.value = []
        } finally {
          schoolsLoading.value = false
        }
      }, 300)
    }
    
    // 学院搜索处理
    const handleCollegeInput = (event) => {
      const keyword = event.target.value.trim()
      
      if (collegeSearchTimer) {
        clearTimeout(collegeSearchTimer)
      }
      
      if (!selectedSchool.value || keyword.length < 1) {
        collegeSuggestions.value = []
        showCollegeSuggestions.value = false
        return
      }
      
      collegeSearchTimer = setTimeout(async () => {
        try {
          collegeLoading.value = true
          showCollegeSuggestions.value = true
          
          const results = await EducationAPI.searchColleges(selectedSchool.value.name, keyword)
          collegeSuggestions.value = results
          console.log(`找到 ${results.length} 个学院:`, results.slice(0, 3))
          
        } catch (error) {
          console.error('学院搜索失败:', error)
          collegeSuggestions.value = []
        } finally {
          collegeLoading.value = false
        }
      }, 300)
    }
    
    // 专业搜索处理
    const handleMajorInput = (event) => {
      const keyword = event.target.value.trim()
      
      if (majorSearchTimer) {
        clearTimeout(majorSearchTimer)
      }
      
      if (!selectedCollege.value || keyword.length < 1) {
        majorSuggestions.value = []
        showMajorSuggestions.value = false
        return
      }
      
      majorSearchTimer = setTimeout(async () => {
        try {
          majorLoading.value = true
          showMajorSuggestions.value = true
          
          const results = await EducationAPI.searchMajors(selectedCollege.value.name, keyword)
          majorSuggestions.value = results
          console.log(`找到 ${results.length} 个专业:`, results.slice(0, 3))
          
        } catch (error) {
          console.error('专业搜索失败:', error)
          majorSuggestions.value = []
        } finally {
          majorLoading.value = false
        }
      }, 300)
    }
    
    // 选择学校
    const selectSchool = (school) => {
      selectedSchool.value = school
      userInfo.education.school = school.name
      schoolSuggestions.value = []
      showSchoolSuggestions.value = false
      
      // 清空学院和专业
      selectedCollege.value = null
      selectedMajor.value = null
      userInfo.education.college = ''
      userInfo.education.major = ''
      
      validateField('school')
      console.log('选择学校:', school)
    }
    
    // 选择学院
    const selectCollege = (college) => {
      selectedCollege.value = college
      userInfo.education.college = college.name
      collegeSuggestions.value = []
      showCollegeSuggestions.value = false
      
      // 清空专业
      selectedMajor.value = null
      userInfo.education.major = ''
      
      validateField('college')
      console.log('选择学院:', college)
    }
    
    // 选择专业
    const selectMajor = (major) => {
      selectedMajor.value = major
      userInfo.education.major = major.name
      majorSuggestions.value = []
      showMajorSuggestions.value = false
      
      validateField('major')
      console.log('选择专业:', major)
    }
    
    // 点击外部关闭建议
    const handleClickOutside = () => {
      showSchoolSuggestions.value = false
      showCollegeSuggestions.value = false
      showMajorSuggestions.value = false
    }
    
    // 头像上传
    const uploadAvatarFile = () => {
      fileInput.value?.click()
    }
    
    // 兼容旧的方法名
    const uploadAvatar = uploadAvatarFile
    
    const handleAvatarUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      // 文件类型验证
      const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']
      if (!allowedTypes.includes(file.type)) {
        errors.avatar = '只支持 PNG、JPG、JPEG、GIF 格式的图片'
        return
      }
      
      // 文件大小验证 (5MB)
      if (file.size > 5 * 1024 * 1024) {
        errors.avatar = '图片大小不能超过5MB'
        return
      }
      
      delete errors.avatar
      
      try {
        const response = await uploadAvatarAPI(file)
        if (response.success) {
          userInfo.avatar = response.avatar_url
          // 同步到auth store
          const updatedUser = { ...authStore.user, avatar: response.avatar_url }
          authStore.setUser(updatedUser)
          console.log('头像上传成功:', response.avatar_url)
        } else {
          errors.avatar = response.message || '头像上传失败'
        }
      } catch (error) {
        console.error('头像上传失败:', error)
        errors.avatar = '头像上传失败，请重试'
      }
    }
    
    // 主要操作
    const toggleEdit = () => {
      if (isEditing.value) {
        // 取消编辑，重新加载数据
        loadPersonalInfo()
        loadEducationInfo()
        // 清除错误和消息
        Object.keys(errors).forEach(key => delete errors[key])
        successMessage.value = ''
        errorMessage.value = ''
        schoolSuggestions.value = []
        collegeSuggestions.value = []
        majorSuggestions.value = []
      } else {
        // 进入编辑状态时清除消息
        successMessage.value = ''
        errorMessage.value = ''
      }
      isEditing.value = !isEditing.value
    }
    
    const saveChanges = async () => {
      // 清除之前的消息
      successMessage.value = ''
      errorMessage.value = ''
      
      saving.value = true
      
      try {
        let savedSections = []
        
        // 只有当基础信息有内容时才保存
        if (userInfo.name || userInfo.gender || userInfo.birthDate || userInfo.phone || userInfo.email || userInfo.contact) {
          const personalData = {
            name: userInfo.name,
            gender: userInfo.gender,
            birth_date: userInfo.birthDate,
            phone: userInfo.phone,
            email: userInfo.email,
            contact: userInfo.contact
          }
          
          const personalResponse = await updatePersonalInfo(personalData)
          
          if (!personalResponse.success) {
            throw new Error(personalResponse.message || '保存个人信息失败')
          }
          
          // 同步用户名和邮箱到auth store
          const updatedUser = { 
            ...authStore.user, 
            name: userInfo.name,
            username: userInfo.name,
            email: userInfo.email 
          }
          authStore.setUser(updatedUser)
          
          savedSections.push('个人信息')
        }
        
        // 只有当教育背景有内容时才保存
        if (userInfo.education.school || userInfo.education.college || userInfo.education.major || userInfo.education.degree) {
          const educationData = {
            school: userInfo.education.school,
            college: userInfo.education.college,
            major: userInfo.education.major,
            degree: userInfo.education.degree,
            start_date: userInfo.education.startDate,
            end_date: userInfo.education.endDate,
            gpa: userInfo.education.gpa,
            courses: userInfo.education.courses
          }
          
          const educationResponse = await updateEducationInfo(educationData)
          
          if (!educationResponse.success) {
            throw new Error(educationResponse.message || '保存教育背景失败')
          }
          
          savedSections.push('教育背景')
        }
        
        // 保存成功
        isEditing.value = false
        
        if (savedSections.length > 0) {
          successMessage.value = `${savedSections.join('、')}保存成功！`
        } else {
          successMessage.value = '保存成功！'
        }
        
        // 重新加载数据确保显示最新信息
        await loadPersonalInfo()
        await loadEducationInfo()
        
        // 3秒后清除成功消息
        setTimeout(() => {
          successMessage.value = ''
        }, 3000)
        
      } catch (error) {
        console.error('保存失败:', error)
        errorMessage.value = error.message || '保存失败，请稍后重试'
        
        // 5秒后清除错误消息
        setTimeout(() => {
          errorMessage.value = ''
        }, 5000)
      } finally {
        saving.value = false
      }
    }
    
    // 实时验证监听
    watch(() => userInfo.email, (newEmail) => {
      if (newEmail && isEditing.value) {
        setTimeout(() => validateField('email'), 300)
      }
    })
    
    watch(() => userInfo.phone, (newPhone) => {
      if (newPhone && isEditing.value) {
        setTimeout(() => validateField('phone'), 300)
      }
    })
    
    return {
      isEditing,
      saving,
      loading,
      successMessage,
      errorMessage,
      userInfo,
      errors,
      authStore,
      
      // 学校相关
      schoolSuggestions,
      schoolsLoading,
      showSchoolSuggestions,
      selectedSchool,
      
      // 学院相关
      collegeSuggestions,
      collegeLoading,
      showCollegeSuggestions,
      selectedCollege,
      
      // 专业相关
      majorSuggestions,
      majorLoading,
      showMajorSuggestions,
      selectedMajor,
      
      // 计算属性
      maxBirthDate,
      maxDate,
      isFormValid,
      
      // DOM引用
      fileInput,
      
      // 方法
      toggleEdit,
      uploadAvatarFile,
      handleAvatarUpload,
      saveChanges,
      validateField,
      handleSchoolInput,
      handleCollegeInput,
      handleMajorInput,
      selectSchool,
      selectCollege,
      selectMajor,
      handleClickOutside,
      handleDegreeChange
    }
  }
}
</script>

<style scoped>
.personal-info {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #86868b;
}

.breadcrumb-item {
  color: #86868b;
}

.breadcrumb-item.active {
  color: #722ED1;
}

.breadcrumb-divider {
  margin: 0 8px;
}

.info-section {
  background: #ffffff;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.edit-btn {
  background: none;
  border: none;
  color: #722ED1;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background-color: #f3f4f6;
}

.info-content {
  padding: 16px 20px;
}

.basic-info-layout {
  display: flex;
  gap: 32px;
  align-items: center;
}

.avatar-section {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 230px;
}

.form-section {
  flex: 1;
}

.avatar-upload {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  border: 2px solid #F3F4F6;
  background-color: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
}

.avatar-upload:hover {
  border-color: #722ED1;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #9ca3af;
}

.avatar-placeholder .svg-icon {
  width: 48px;
  height: 48px;
  color: #722ED1;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #86868b;
  text-align: center;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  position: relative;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 3px;
}

.required {
  color: #ef4444;
  margin-left: 2px;
}

.form-input, .form-select, .form-textarea {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.2s ease;
  background-color: #ffffff;
  height: 36px;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #722ED1;
  box-shadow: 0 0 0 3px rgba(114, 45, 209, 0.1);
}

.form-input:disabled, .form-select:disabled, .form-textarea:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-input::placeholder, .form-textarea::placeholder {
  color: #9ca3af;
}

.form-input.error, .form-select.error, .form-textarea.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.2;
}

.date-input {
  color-scheme: light;
  height: 36px !important;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-separator {
  color: #6b7280;
  font-size: 14px;
}

.form-textarea {
  resize: vertical;
  min-height: 36px;
  height: 60px;
}

.autocomplete-wrapper {
  position: relative;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-top: none;
  border-radius: 0 0 6px 6px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.suggestion-item {
  padding: 10px 12px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.2s ease;
}

.suggestion-item:hover {
  background-color: #f3f4f6;
}

.suggestion-item:last-child {
  border-radius: 0 0 6px 6px;
}

.suggestion-more {
  padding: 8px 12px;
  font-size: 12px;
  color: #6b7280;
  background-color: #f9fafb;
  text-align: center;
  border-top: 1px solid #f0f0f0;
}

.loading-indicator {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-top: none;
  border-radius: 0 0 6px 6px;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.loading-text {
  padding: 12px;
  text-align: center;
  font-size: 13px;
  color: #722ED1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-text::before {
  content: '';
  width: 16px;
  height: 16px;
  border: 2px solid #f3f4f6;
  border-top: 2px solid #722ED1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.school-info, .college-info, .major-info {
  width: 100%;
}

.school-name, .college-name, .major-name {
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 2px;
}

.school-detail, .college-detail, .major-detail {
  font-size: 12px;
  color: #86868b;
  line-height: 1.3;
}

.save-section {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.save-btn {
  background: linear-gradient(135deg, #722ED1 0%, #722ED1 100%);
  color: #ffffff;
  border: none;
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(114, 45, 209, 0.3);
}

.save-btn.active {
  background: linear-gradient(135deg, #722ED1 0%, #5B21B6 100%);
  box-shadow: 0 6px 16px rgba(114, 45, 209, 0.4);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(114, 45, 209, 0.4);
}

.save-btn:active:not(:disabled) {
  transform: translateY(0);
}

.save-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.message {
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  animation: fadeIn 0.3s ease-in-out;
}

.success-message {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.error-message {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>