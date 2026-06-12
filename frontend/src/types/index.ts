// 岗位相关类型
export enum EmploymentType {
  FULL_TIME = 'full-time',
  PART_TIME = 'part-time',
  CONTRACT = 'contract',
  INTERNSHIP = 'internship',
}

export enum JobStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  PAUSED = 'paused',
  CLOSED = 'closed',
}

export interface SalaryRange {
  min: number
  max: number
  currency: string
}

export interface JobRequirements {
  education: string | null
  min_experience_years: number
  required_skills: string[]
  preferred_skills: string[]
  languages: string[]
  other: string
}

export interface Job {
  id: string
  title: string
  department: string
  location: string
  employment_type: EmploymentType
  description: string
  responsibilities: string[]
  requirements: JobRequirements
  salary_range: SalaryRange | null
  status: JobStatus
  tags: string[]
  application_count: number
  created_at: string
  updated_at: string
}

export interface JobCreate {
  title: string
  department?: string
  location: string
  employment_type?: EmploymentType
  description: string
  responsibilities?: string[]
  requirements?: Partial<JobRequirements>
  salary_range?: SalaryRange
  status?: JobStatus
  tags?: string[]
}

export interface JobUpdate extends Partial<JobCreate> {}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 设置相关
export interface SettingsResponse {
  deepseek_api_key_set: boolean
  deepseek_api_key_masked: string
  deepseek_base_url: string
  deepseek_model: string
  language: string
  theme: string
}

export interface APITestResponse {
  success: boolean
  message: string
  model: string
}
