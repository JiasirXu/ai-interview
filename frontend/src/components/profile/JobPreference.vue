<template>
  <div class="job-preference">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item">个人中心</span>
      <span class="breadcrumb-divider">></span>
      <span class="breadcrumb-item active">岗位偏好</span>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <h3 class="section-title">选择目标领域 <span class="required">*</span></h3>
    </div>

    <!-- 目标领域选择 -->
    <div class="target-fields">
      <div 
        v-for="field in targetFields" 
        :key="field.id"
        class="field-card"
        :class="{ active: selectedField === field.id }"
        @click="selectField(field.id)"
      >
        <div class="field-icon">
          <SvgIcon :name="field.icon" />
        </div>
        <div class="field-info">
          <h3 class="field-name">{{ field.name }}</h3>
          <p class="field-salary">平均薪资：{{ field.salary }}</p>
        </div>
      </div>
    </div>

    <!-- 选择岗位方向 -->
    <div class="position-direction" v-if="selectedField">
      <h3 class="section-title">
        选择岗位方向 <span class="required">*</span> <span class="optional">（最多选择3个）</span>
      </h3>
      <div class="direction-buttons">
        <button
          v-for="position in availablePositions"
          :key="position.value"
          class="direction-btn"
          :class="{ active: selectedDirections.includes(position.value) }"
          @click="toggleDirection(position.value)"
          :disabled="!selectedDirections.includes(position.value) && selectedDirections.length >= 3"
        >
          {{ position.label }}
        </button>
      </div>
      <div class="selection-hint" v-if="selectedDirections.length === 0">
        请选择您感兴趣的岗位方向
      </div>
    </div>

    <!-- 目标企业 -->
    <div class="target-companies">
      <h3 class="section-title">目标企业 <span class="optional">（最多添加15家企业）</span></h3>
      <div class="company-tags">
        <span 
          v-for="(company, index) in selectedCompanies" 
          :key="index"
          class="company-tag"
        >
          {{ company }}
          <span class="remove-tag" @click="removeCompany(index)">×</span>
        </span>
        <button class="add-company-btn" @click="showAddCompany = true">+ 添加企业</button>
      </div>
      
      <!-- 添加企业输入框 -->
      <div v-if="showAddCompany" class="add-company-input">
        <input 
          v-model="newCompany"
          type="text" 
          placeholder="请输入企业名称"
          @keyup.enter="addCompany"
          @blur="hideAddCompany"
          ref="companyInput"
        />
        <button @click="addCompany" class="confirm-add">确定</button>
        <button @click="hideAddCompany" class="cancel-add">取消</button>
      </div>
    </div>

    <!-- 工作地点 -->
    <div class="work-location">
      <h3 class="section-title">
        工作地点 <span class="required">*</span>
      </h3>
      <div class="location-selector">
        <div class="location-dropdown" @click="toggleCityDropdown">
          <span class="location-text">{{ selectedCity || '选择城市' }}</span>
          <span class="dropdown-icon" :class="{ open: showCityDropdown }">⌄</span>
        </div>
        <div v-if="showCityDropdown" class="city-dropdown">
          <div class="city-search">
            <input 
              v-model="citySearchQuery"
              type="text"
              placeholder="搜索城市"
              @input="filterCities"
            />
          </div>
          <div class="city-list">
            <div 
              v-for="city in filteredCities"
              :key="city"
              class="city-option"
              @click="selectCity(city)"
            >
              {{ city }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 公司规模 -->
    <div class="company-size">
      <h3 class="section-title">公司规模</h3>
      <div class="size-buttons">
        <button
          v-for="size in companySizes"
          :key="size.value"
          class="size-btn"
          :class="{ active: selectedCompanySize === size.value }"
          @click="selectCompanySize(size.value)"
        >
          {{ size.label }}
        </button>
      </div>
    </div>

    <!-- 工作经验 -->
    <div class="work-experience">
      <h3 class="section-title">工作经验</h3>
      <div class="experience-selector">
        <select v-model="selectedExperience" class="experience-select">
          <option value="">不限</option>
          <option value="0-1">0-1年</option>
          <option value="1-3">1-3年</option>
          <option value="3-5">3-5年</option>
          <option value="5+">5年以上</option>
        </select>
        <span class="dropdown-icon">⌄</span>
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="bottom-actions">
      <button class="save-btn" @click="saveSettings">保存设置</button>
      <button class="reset-btn" @click="resetSettings">重置</button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import SvgIcon from '../common/SvgIcon.vue'
import {
  getJobPreferences,
  updateJobPreferences
} from '@/api/preference'

export default {
  name: 'JobPreference',
  components: {
    SvgIcon
  },
  setup() {
    const isEditing = ref(false)
    const saving = ref(false)
    
    // 原有的数据结构，保持与模板兼容
    const selectedField = ref(null)
    const selectedDirections = ref([])
    const selectedCompanySize = ref('')
    const selectedExperience = ref('')
    const selectedCompanies = ref(['腾讯', '字节跳动'])
    const showAddCompany = ref(false)
    const newCompany = ref('')
    const selectedCity = ref('')
    const showCityDropdown = ref(false)
    const citySearchQuery = ref('')
    
    // 职业配置数据
    const targetFields = ref([])
    const availablePositions = ref([])

    // 加载职业配置
    const loadCareerConfig = async () => {
      try {
        const token = localStorage.getItem('access_token')
        console.log('发送请求的token:', token ? `存在，长度: ${token.length}` : '不存在')
        console.log('Token内容:', token)

        if (!token) {
          console.error('没有找到token，请先登录')
          return
        }

        const response = await fetch('/api/preferences/career-config', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          console.log('职业配置API响应:', data)
          if (data.success) {
            targetFields.value = data.data.target_fields.map(field => ({
              id: field.value,
              name: field.label,
              salary: field.salary_range,
              icon: field.value === 'ai' ? 'work' : field.value === 'big_data' ? 'database' : 'network',
              positions: field.positions
            }))
            console.log('处理后的目标领域:', targetFields.value)
          } else {
            console.error('API返回失败:', data.message)
          }
        } else {
          console.error('API请求失败:', response.status, response.statusText)
          const errorData = await response.json().catch(() => ({}))
          console.error('错误详情:', errorData)
        }
      } catch (error) {
        console.error('加载职业配置失败:', error)
        // 使用默认配置
        console.log('使用默认职业配置')
        targetFields.value = [
          {
            id: 'ai',
            name: '人工智能',
            salary: '18-35K/月',
            icon: 'work',
            positions: [
              {value: 'ai_algorithm_engineer', label: 'AI算法工程师'},
              {value: 'machine_learning_engineer', label: '机器学习工程师'},
              {value: 'ai_product_manager', label: 'AI产品经理'},
              {value: 'ai_data_scientist', label: 'AI数据科学家'}
            ]
          },
          {
            id: 'big_data',
            name: '大数据',
            salary: '15-30K/月',
            icon: 'database',
            positions: [
              {value: 'big_data_engineer', label: '大数据开发工程师'},
              {value: 'data_analyst', label: '数据分析师'},
              {value: 'data_product_manager', label: '数据产品经理'},
              {value: 'data_architect', label: '数据架构师'}
            ]
          },
          {
            id: 'iot',
            name: '物联网',
            salary: '12-25K/月',
            icon: 'network',
            positions: [
              {value: 'iot_engineer', label: '物联网开发工程师'},
              {value: 'iot_system_engineer', label: '物联网系统工程师'},
              {value: 'iot_product_manager', label: '物联网产品经理'},
              {value: 'iot_solution_architect', label: '物联网解决方案架构师'}
            ]
          }
        ]
      }
    }

    // 加载用户职业偏好
    const loadCareerPreferences = async () => {
      try {
        const response = await fetch('/api/preferences/career', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            const preferences = data.data
            selectedField.value = preferences.target_field || 'ai'
            selectedDirections.value = preferences.target_positions || []
            selectedCompanies.value = preferences.target_companies || []
            selectedCity.value = preferences.work_location || ''
            selectedCompanySize.value = preferences.company_size || ''
            selectedExperience.value = preferences.work_experience || ''

            // 更新可用岗位
            const field = targetFields.value.find(f => f.id === selectedField.value)
            if (field) {
              availablePositions.value = field.positions || []
            }

            console.log('加载的职业偏好:', preferences)
          }
        }
      } catch (error) {
        console.error('加载职业偏好失败:', error)
      }
    }
    
    const directions = ref(['技术开发', '产品经理', '测试运维', '数据分析'])
    
    const companySizes = ref([
      { value: 'startup', label: '初创公司（<100人）' },
      { value: 'medium', label: '中型企业（100-1000人）' },
      { value: 'large', label: '大型企业（>1000人）' }
    ])
    
    const cities = ref([
      // 直辖市
      '北京', '上海', '天津', '重庆',
      // 华北地区
      '石家庄', '唐山', '秦皇岛', '邯郸', '邢台', '保定', '张家口', '承德', '沧州', '廊坊', '衡水',
      '太原', '大同', '阳泉', '长治', '晋城', '朔州', '晋中', '运城', '忻州', '临汾', '吕梁',
      '呼和浩特', '包头', '乌海', '赤峰', '通辽', '鄂尔多斯', '呼伦贝尔', '巴彦淖尔', '乌兰察布',
      // 东北地区
      '沈阳', '大连', '鞍山', '抚顺', '本溪', '丹东', '锦州', '营口', '阜新', '辽阳', '盘锦', '铁岭', '朝阳', '葫芦岛',
      '长春', '吉林', '四平', '辽源', '通化', '白山', '松原', '白城',
      '哈尔滨', '齐齐哈尔', '鸡西', '鹤岗', '双鸭山', '大庆', '伊春', '佳木斯', '七台河', '牡丹江', '黑河', '绥化',
      // 华东地区
      '南京', '无锡', '徐州', '常州', '苏州', '南通', '连云港', '淮安', '盐城', '扬州', '镇江', '泰州', '宿迁',
      '杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水',
      '合肥', '芜湖', '蚌埠', '淮南', '马鞍山', '淮北', '铜陵', '安庆', '黄山', '阜阳', '宿州', '滁州', '六安', '宣城', '池州', '亳州',
      '福州', '厦门', '莆田', '三明', '泉州', '漳州', '南平', '龙岩', '宁德',
      '南昌', '景德镇', '萍乡', '九江', '抚州', '鹰潭', '赣州', '吉安', '宜春', '新余', '上饶',
      '济南', '青岛', '淄博', '枣庄', '东营', '烟台', '潍坊', '济宁', '泰安', '威海', '日照', '临沂', '德州', '聊城', '滨州', '菏泽',
      // 中南地区
      '郑州', '开封', '洛阳', '平顶山', '安阳', '鹤壁', '新乡', '焦作', '濮阳', '许昌', '漯河', '三门峡', '南阳', '商丘', '信阳', '周口', '驻马店',
      '武汉', '黄石', '十堰', '宜昌', '襄阳', '鄂州', '荆门', '孝感', '荆州', '黄冈', '咸宁', '随州',
      '长沙', '株洲', '湘潭', '衡阳', '邵阳', '岳阳', '常德', '张家界', '益阳', '郴州', '永州', '怀化', '娄底',
      '广州', '韶关', '深圳', '珠海', '汕头', '佛山', '江门', '湛江', '茂名', '肇庆', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮',
      '南宁', '柳州', '桂林', '梧州', '北海', '防城港', '钦州', '贵港', '玉林', '百色', '贺州', '河池', '来宾', '崇左',
      '海口', '三亚', '三沙', '儋州',
      // 西南地区
      '成都', '自贡', '攀枝花', '泸州', '德阳', '绵阳', '广元', '遂宁', '内江', '乐山', '南充', '眉山', '宜宾', '广安', '达州', '雅安', '巴中', '资阳',
      '贵阳', '六盘水', '遵义', '安顺', '毕节', '铜仁',
      '昆明', '曲靖', '玉溪', '保山', '昭通', '丽江', '普洱', '临沧',
      '拉萨', '日喀则', '昌都', '林芝', '山南', '那曲',
      // 西北地区
      '西安', '铜川', '宝鸡', '咸阳', '渭南', '延安', '汉中', '榆林', '安康', '商洛',
      '兰州', '嘉峪关', '金昌', '白银', '天水', '武威', '张掖', '平凉', '酒泉', '庆阳', '定西', '陇南',
      '西宁', '海东',
      '银川', '石嘴山', '吴忠', '固原', '中卫'
    ])
    
    const filteredCities = ref([...cities.value])
    
    // 新的验证数据结构
    const jobPreference = reactive({
      targetPosition: '',
      targetIndustry: [],
      expectedSalary: {
        min: null,
        max: null,
        currency: 'CNY'
      },
      workType: '',
      workLocation: [],
      skills: [],
      workExperience: '',
      jobDescription: '',
      availability: ''
    })
    
    const errors = reactive({})
    const positionSuggestions = ref([])
    const skillSuggestions = ref([])
    const skillInput = ref('')
    const newSkill = ref('')
    
    // 常用职位数据
    const commonPositions = [
      '前端工程师', '后端工程师', '全栈工程师', 'Java工程师', 'Python工程师',
      'Android工程师', 'iOS工程师', '测试工程师', '运维工程师', '算法工程师',
      '数据分析师', '产品经理', 'UI设计师', 'UX设计师', '项目经理'
    ]
    
    // 常用技能数据
    const commonSkills = [
      'Vue.js', 'React', 'Angular', 'JavaScript', 'TypeScript', 'HTML5', 'CSS3',
      'Java', 'Spring Boot', 'Python', 'Django', 'Flask', 'Node.js', 'Express',
      'MySQL', 'MongoDB', 'Redis', 'Git', 'Docker', 'Kubernetes', 'Linux'
    ]
    
    // 行业选项
    const industryOptions = [
      { icon: 'container1', label: '互联网', value: '互联网' },
      { icon: 'container2', label: '金融', value: '金融' },
      { icon: 'container3', label: '教育', value: '教育' },
      { icon: 'container4', label: '医疗', value: '医疗' },
      { icon: 'container5', label: '电商', value: '电商' },
      { icon: 'container6', label: '游戏', value: '游戏' },
      { icon: 'container7', label: 'AI/机器学习', value: 'AI/机器学习' },
      { icon: 'container8', label: '区块链', value: '区块链' },
      { icon: 'container9', label: '物联网', value: '物联网' }
    ]
    
    // 工作地点选项
    const locationOptions = ['北京', '上海', '深圳', '广州', '杭州', '成都', '南京', '武汉', '西安', '重庆']
    
    // 计算属性
    const isFormValid = computed(() => {
      return Object.keys(errors).length === 0 && 
             jobPreference.targetPosition && 
             jobPreference.targetIndustry.length > 0 &&
             jobPreference.expectedSalary.min &&
             jobPreference.expectedSalary.max &&
             jobPreference.workType &&
             jobPreference.workLocation.length > 0 &&
             jobPreference.workExperience &&
             jobPreference.availability
    })
    
    const salaryRangeText = computed(() => {
      const { min, max } = jobPreference.expectedSalary
      if (min && max) {
        return `${min}k - ${max}k`
      }
      return ''
    })
    
    // 原有的方法，保持与模板兼容
    const selectField = (fieldId) => {
      selectedField.value = fieldId
      // 清空之前选择的岗位方向
      selectedDirections.value = []
      // 更新可用岗位
      const field = targetFields.value.find(f => f.id === fieldId)
      if (field) {
        availablePositions.value = field.positions || []
      }
    }
    
    const toggleDirection = (direction) => {
      const index = selectedDirections.value.indexOf(direction)
      if (index > -1) {
        selectedDirections.value.splice(index, 1)
      } else if (selectedDirections.value.length < 3) {
        selectedDirections.value.push(direction)
      }
    }
    
    const removeCompany = (index) => {
      selectedCompanies.value.splice(index, 1)
    }
    
    const addCompany = () => {
      if (newCompany.value.trim() && selectedCompanies.value.length < 15) {
        selectedCompanies.value.push(newCompany.value.trim())
        newCompany.value = ''
        showAddCompany.value = false
      }
    }
    
    const hideAddCompany = () => {
      setTimeout(() => {
        showAddCompany.value = false
        newCompany.value = ''
      }, 200)
    }
    
    const toggleCityDropdown = () => {
      showCityDropdown.value = !showCityDropdown.value
      if (showCityDropdown.value) {
        citySearchQuery.value = ''
        filteredCities.value = [...cities.value]
      }
    }
    
    const selectCity = (city) => {
      selectedCity.value = city
      showCityDropdown.value = false
    }
    
    const selectCompanySize = (size) => {
      selectedCompanySize.value = size
    }
    
    const filterCities = () => {
      if (citySearchQuery.value.trim()) {
        filteredCities.value = cities.value.filter(city => 
          city.includes(citySearchQuery.value.trim())
        )
      } else {
        filteredCities.value = [...cities.value]
      }
    }
    
    const saveSettings = async () => {
      if (!selectedField.value) {
        alert('请选择目标领域')
        return
      }

      if (selectedDirections.value.length === 0) {
        alert('请至少选择一个岗位方向')
        return
      }

      if (!selectedCity.value) {
        alert('请选择工作地点')
        return
      }

      try {
        const response = await fetch('/api/preferences/career', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({
            target_field: selectedField.value,
            target_positions: selectedDirections.value,
            target_companies: selectedCompanies.value,
            work_location: selectedCity.value,
            company_size: selectedCompanySize.value,
            work_experience: selectedExperience.value
          })
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            const savedData = data.data
            console.log('保存成功:', savedData)

            // 显示详细的保存信息
            const fieldLabel = targetFields.value.find(f => f.id === savedData.target_field)?.name || savedData.target_field
            const positionLabels = savedData.target_positions.map(pos => {
              const field = targetFields.value.find(f => f.id === savedData.target_field)
              return field?.positions?.find(p => p.value === pos)?.label || pos
            }).join('、')

            alert(`职业偏好保存成功！\n目标领域：${fieldLabel}\n选择岗位：${positionLabels}`)
          } else {
            alert('保存失败：' + data.message)
          }
        } else {
          alert('保存失败，请稍后重试')
        }
      } catch (error) {
        console.error('保存职业偏好失败:', error)
        alert('保存失败，请检查网络连接')
      }
    }
    
    const resetSettings = () => {
      selectedField.value = null
      selectedDirections.value = []
      selectedCompanies.value = []
      selectedCity.value = ''
      selectedCompanySize.value = ''
      selectedExperience.value = ''
    }
    
    // 验证方法
    const validateField = (field) => {
      delete errors[field]
      
      switch (field) {
        case 'targetPosition':
          if (!jobPreference.targetPosition) {
            errors.targetPosition = '目标职位不能为空'
          } else if (jobPreference.targetPosition.length > 50) {
            errors.targetPosition = '职位名称不能超过50个字符'
          }
          break
          
        case 'targetIndustry':
          if (jobPreference.targetIndustry.length === 0) {
            errors.targetIndustry = '请至少选择一个目标行业'
          } else if (jobPreference.targetIndustry.length > 3) {
            errors.targetIndustry = '最多只能选择3个行业'
          }
          break
          
        case 'expectedSalary':
          const { min, max } = jobPreference.expectedSalary
          if (!min || !max) {
            errors.expectedSalary = '请输入期望薪资范围'
          } else if (min <= 0 || max <= 0) {
            errors.expectedSalary = '薪资必须大于0'
          } else if (min >= max) {
            errors.expectedSalary = '最高薪资必须大于最低薪资'
          } else if (max > 1000) {
            errors.expectedSalary = '薪资范围请输入合理数值'
          }
          break
          
        case 'workType':
          if (!jobPreference.workType) {
            errors.workType = '请选择工作类型'
          }
          break
          
        case 'workLocation':
          if (jobPreference.workLocation.length === 0) {
            errors.workLocation = '请至少选择一个工作地点'
          } else if (jobPreference.workLocation.length > 5) {
            errors.workLocation = '最多只能选择5个工作地点'
          }
          break
          
        case 'workExperience':
          if (!jobPreference.workExperience) {
            errors.workExperience = '请选择工作经验'
          }
          break
          
        case 'jobDescription':
          if (jobPreference.jobDescription.length > 500) {
            errors.jobDescription = '职位描述不能超过500个字符'
          }
          break
          
        case 'availability':
          if (!jobPreference.availability) {
            errors.availability = '请选择到岗时间'
          }
          break
      }
    }
    
    const validateAllFields = () => {
      const fields = ['targetPosition', 'targetIndustry', 'expectedSalary', 'workType', 'workLocation', 'workExperience', 'availability', 'jobDescription']
      fields.forEach(field => validateField(field))
    }
    
    // 智能搜索
    const searchPositions = (event) => {
      const keyword = event.target.value
      if (keyword.length < 2) {
        positionSuggestions.value = []
        return
      }
      
      positionSuggestions.value = commonPositions
        .filter(position => position.includes(keyword))
        .slice(0, 8)
    }
    
    const searchSkills = () => {
      const keyword = newSkill.value
      if (keyword.length < 2) {
        skillSuggestions.value = []
        return
      }
      
      skillSuggestions.value = commonSkills
        .filter(skill => 
          skill.toLowerCase().includes(keyword.toLowerCase()) &&
          !jobPreference.skills.includes(skill)
        )
        .slice(0, 8)
    }
    
    const selectPosition = (position) => {
      jobPreference.targetPosition = position
      positionSuggestions.value = []
      validateField('targetPosition')
    }
    
    const selectSkill = (skill) => {
      if (!jobPreference.skills.includes(skill)) {
        jobPreference.skills.push(skill)
      }
      newSkill.value = ''
      skillSuggestions.value = []
    }
    
    // 行业选择
    const toggleIndustry = (industry) => {
      const index = jobPreference.targetIndustry.indexOf(industry)
      if (index > -1) {
        jobPreference.targetIndustry.splice(index, 1)
      } else {
        if (jobPreference.targetIndustry.length < 3) {
          jobPreference.targetIndustry.push(industry)
        }
      }
      validateField('targetIndustry')
    }
    
    // 工作地点选择
    const toggleLocation = (location) => {
      const index = jobPreference.workLocation.indexOf(location)
      if (index > -1) {
        jobPreference.workLocation.splice(index, 1)
      } else {
        if (jobPreference.workLocation.length < 5) {
          jobPreference.workLocation.push(location)
        }
      }
      validateField('workLocation')
    }
    
    // 技能管理
    const addSkill = () => {
      const skill = newSkill.value.trim()
      if (skill && !jobPreference.skills.includes(skill)) {
        if (jobPreference.skills.length < 20) {
          jobPreference.skills.push(skill)
          newSkill.value = ''
          skillSuggestions.value = []
        }
      }
    }
    
    const removeSkill = (skill) => {
      const index = jobPreference.skills.indexOf(skill)
      if (index > -1) {
        jobPreference.skills.splice(index, 1)
      }
    }
    
    // 薪资验证
    const validateSalaryRange = () => {
      validateField('expectedSalary')
    }
    
    // 主要操作
    const toggleEdit = () => {
      if (isEditing.value) {
        // 取消编辑，清除错误
        Object.keys(errors).forEach(key => delete errors[key])
        positionSuggestions.value = []
        skillSuggestions.value = []
      }
      isEditing.value = !isEditing.value
    }
    
    const saveChanges = async () => {
      validateAllFields()
      
      if (!isFormValid.value) {
        return
      }
      
      saving.value = true
      
      try {
        // 这里调用API保存数据
        console.log('保存求职偏好:', jobPreference)
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        isEditing.value = false
        // 显示成功提示
        console.log('保存成功')
        
      } catch (error) {
        console.error('保存失败:', error)
        // 显示错误提示
      } finally {
        saving.value = false
      }
    }
    
    // 实时验证监听
    watch(() => jobPreference.expectedSalary, () => {
      if (isEditing.value) {
        setTimeout(() => validateField('expectedSalary'), 300)
      }
    }, { deep: true })
    
    watch(() => newSkill.value, () => {
      searchSkills()
    })

    // 初始化数据
    onMounted(async () => {
      await loadCareerConfig()
      await loadCareerPreferences()
    })

    return {
      // 原有模板需要的变量
      selectedField,
      selectedDirections,
      selectedCompanySize,
      selectedExperience,
      selectedCompanies,
      showAddCompany,
      newCompany,
      selectedCity,
      showCityDropdown,
      citySearchQuery,
      targetFields,
      availablePositions,
      directions,
      companySizes,
      cities,
      filteredCities,
      
      // 原有模板需要的方法
      selectField,
      toggleDirection,
      removeCompany,
      addCompany,
      hideAddCompany,
      toggleCityDropdown,
      selectCity,
      selectCompanySize,
      filterCities,
      saveSettings,
      resetSettings,
      
      // 新增的验证功能
      isEditing,
      saving,
      jobPreference,
      errors,
      positionSuggestions,
      skillSuggestions,
      skillInput,
      newSkill,
      industryOptions,
      locationOptions,
      isFormValid,
      salaryRangeText,
      toggleEdit,
      saveChanges,
      validateField,
      validateSalaryRange,
      searchPositions,
      searchSkills,
      selectPosition,
      selectSkill,
      toggleIndustry,
      toggleLocation,
      addSkill,
      removeSkill
    }
  }
}
</script>

<style scoped>
.job-preference {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

/* 面包屑导航 */
.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
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

.page-header {
  margin-bottom: 40px;
}

.section-title {
  font-size: 18px;
  font-weight: 500;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.section-subtitle {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.required {
  color: #ef4444;
}

.optional {
  font-size: 14px;
  font-weight: 400;
  color: #6b7280;
}

/* 目标领域卡片 */
.target-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.field-card {
  display: flex;
  align-items: center;
  padding: 24px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #ffffff;
}

.field-card:hover {
  border-color: #722ED1;
  box-shadow: 0 4px 12px rgba(114, 45, 209, 0.1);
}

.field-card.active {
  border-color: #722ED1;
  background: linear-gradient(135deg, #f3f0ff 0%, #ede9fe 100%);
}

.field-icon {
  width: 48px;
  height: 48px;
  margin-right: 16px;
  flex-shrink: 0;
  color: #722ED1;
}

.field-info {
  flex: 1;
}

.field-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.field-salary {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* 岗位方向选择 */
.position-direction {
  margin-bottom: 40px;
}

.direction-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.direction-btn {
  padding: 12px 24px;
  border: 1px solid #d1d5db;
  border-radius: 24px;
  background: #ffffff;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.direction-btn:hover {
  border-color: #722ED1;
  color: #722ED1;
}

.direction-btn.active {
  background: linear-gradient(135deg, #f3f0ff 0%, #ede9fe 100%);
  border-color: #722ED1;
  color: #722ED1;
}

/* 目标企业 */
.target-companies {
  margin-bottom: 40px;
}

.company-info {
  margin-bottom: 16px;
}

.company-count {
  font-size: 14px;
  color: #6b7280;
}

.company-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.company-tag {
  padding: 8px 16px;
  background: #f3f4f6;
  border-radius: 20px;
  font-size: 14px;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.remove-tag {
  cursor: pointer;
  color: #9ca3af;
  font-weight: bold;
}

.remove-tag:hover {
  color: #ef4444;
}

.add-company-btn {
  padding: 8px 16px;
  border: 1px dashed #722ED1;
  border-radius: 20px;
  background: none;
  color: #722ED1;
  font-size: 14px;
  cursor: pointer;
}

.add-company-input {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 16px;
}

.add-company-input input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  flex: 1;
  max-width: 200px;
}

.confirm-add, .cancel-add {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  font-size: 14px;
  cursor: pointer;
}

.confirm-add {
  background: #722ED1;
  color: #ffffff;
  border-color: #722ED1;
}

/* 工作地点 */
.work-location {
  margin-bottom: 40px;
  position: relative;
}

.location-selector {
  position: relative;
}

.location-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #ffffff;
  color: #374151;
  font-size: 16px;
  cursor: pointer;
  min-width: 200px;
  transition: border-color 0.2s ease;
}

.location-dropdown:hover {
  border-color: #722ED1;
}

.location-icon {
  font-size: 16px;
}

.location-text {
  flex: 1;
  color: #374151;
}

.dropdown-icon {
  font-size: 18px;
  color: #9ca3af;
  transition: transform 0.2s ease;
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.city-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 300px;
  overflow: hidden;
}

.city-search {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.city-search input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.city-list {
  max-height: 200px;
  overflow-y: auto;
}

.city-option {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.city-option:hover {
  background-color: #f3f4f6;
}

/* 公司规模 */
.company-size {
  margin-bottom: 40px;
}

.size-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.size-btn {
  padding: 12px 24px;
  border: 1px solid #d1d5db;
  border-radius: 24px;
  background: #ffffff;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.size-btn:hover {
  border-color: #722ED1;
  color: #722ED1;
}

.size-btn.active {
  background: linear-gradient(135deg, #f3f0ff 0%, #ede9fe 100%);
  border-color: #722ED1;
  color: #722ED1;
}

/* 工作经验 */
.work-experience {
  margin-bottom: 60px;
}

.experience-selector {
  position: relative;
  display: inline-block;
}

.experience-select {
  padding: 12px 40px 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #ffffff;
  font-size: 16px;
  color: #374151;
  cursor: pointer;
  appearance: none;
  min-width: 200px;
}

.experience-selector .dropdown-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

/* 底部按钮 */
.bottom-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-start;
}

.save-btn {
  padding: 14px 32px;
  background: #722ED1;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.save-btn:hover {
  background: #5A1F9F;
}

.reset-btn {
  padding: 14px 32px;
  background: none;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reset-btn:hover {
  color: #374151;
  border-color: #9ca3af;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .target-fields {
    grid-template-columns: 1fr;
  }
  
  .direction-buttons {
    justify-content: flex-start;
  }
  
  .size-options {
    flex-direction: column;
    gap: 16px;
  }
  
  .bottom-actions {
    flex-direction: column;
  }
  
  .save-btn, .reset-btn {
    width: 100%;
  }
}

/* 新增样式 */
.selection-hint {
  margin-top: 12px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  color: #6c757d;
  font-size: 14px;
  text-align: center;
}



.direction-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f5f5f5;
  color: #999;
}

.direction-btn:disabled:hover {
  background-color: #f5f5f5;
  color: #999;
}
</style> 