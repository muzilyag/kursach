import { ref, reactive, watch, onMounted, computed } from 'vue'

export type SortOrder = 'asc' | 'desc'

export interface DataTableParams {
  page: number
  limit: number
  search: string
  sort: string
  order: SortOrder
  [key: string]: any
}

export function useDataTable(fetchFn: (params: any) => Promise<any>, initialParams: Partial<DataTableParams> = {}) {
  const items = ref<any[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref('')

  const params = reactive<DataTableParams>({
    page: 1,
    limit: 10,
    search: '',
    sort: '',
    order: 'desc',
    ...initialParams
  })

  const load = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await fetchFn({ ...params })
      items.value = response.users || response.content || response.subscriptions || response.items || []
      total.value = response.total || 0
    } catch (e: any) {
      error.value = e.message || 'Ошибка загрузки данных'
    } finally {
      loading.value = false
    }
  }

  const pages = computed(() => {
    const totalPages = Math.ceil(total.value / params.limit)
    return Array.from({ length: totalPages }, (_, i) => i + 1)
  })

  const handleSort = (key: string) => {
    if (params.sort === key) {
      params.order = params.order === 'asc' ? 'desc' : 'asc'
    } else {
      params.sort = key
      params.order = 'asc'
    }
    params.page = 1
    load()
  }

  watch(() => params.page, load)

  onMounted(load)

  return {
    items,
    total,
    loading,
    error,
    params,
    pages,
    load,
    handleSort
  }
}