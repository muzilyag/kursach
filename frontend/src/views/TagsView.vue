<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { ApiService } from '../services/api'
import { Config } from '../config'
import type { ITag, IPopularTag } from '../services/api'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import SidePanel from '../components/SidePanel.vue'
import CheckboxList from '../components/CheckboxList.vue'

const columns = [
  { key: 'tag_name', label: 'Название тега', sortable: true },
  { key: 'count', label: 'Кол-во контента', sortable: true },
  { key: 'views_count', label: 'Просмотры', sortable: true }
]

const isEditing = ref(false)
const currentId = ref<number | null>(null)
const isPanelOpen = ref(false)
const tagForm = reactive({
  tag_name: '',
  content_ids: [] as number[]
})

const tagCounts = ref<Record<number, number>>({})
const allTags = ref<ITag[]>([])
const allContent = ref<any[]>([])
const popularTags = ref<IPopularTag[]>([])

const cloudWidth = ref(40)
const topCloudHeight = ref(50)
const isResizing = ref(false)
const isResizingVertical = ref(false)

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getTagsDirect(p),
  { sort: 'tag_id', order: 'desc', limit: Config.pagination.itemsPerPage }
)

const tagViewsMap = computed(() => {
  const map: Record<string, number> = {}
  popularTags.value.forEach((t) => {
    map[t.tag_name] = t.views_count
  })
  return map
})

const cloudTags = computed(() => {
  const sorted = [...allTags.value].sort((a, b) => {
    const countA = tagCounts.value[a.tag_id] || 0
    const countB = tagCounts.value[b.tag_id] || 0
    return countB - countA
  })

  const result: ITag[] = []
  sorted.forEach((tag, index) => {
    if (index % 2 === 0) {
      result.push(tag)
    } else {
      result.unshift(tag)
    }
  })
  return result
})

const maxViews = computed(() => {
  return popularTags.value.length ? Math.max(...popularTags.value.map((t) => t.views_count)) : 1
})
const minViews = computed(() => {
  return popularTags.value.length ? Math.min(...popularTags.value.map((t) => t.views_count)) : 0
})

const loadStatsAndTags = async () => {
  try {
    const [tags, contentData, popular] = await Promise.all([
      ApiService.getTags(),
      ApiService.getContent({ limit: 10000 }),
      ApiService.getPopularTags(50).catch(() => [])
    ])

    allTags.value = tags
    allContent.value = contentData.items
    popularTags.value = popular

    const counts: Record<number, number> = {}
    contentData.items.forEach((c) => {
      c.tags?.forEach((t) => {
        counts[t.tag_id] = (counts[t.tag_id] || 0) + 1
      })
    })
    tagCounts.value = counts
  } catch {}
}

const getTagStyle = (tagId: number) => {
  const count = tagCounts.value[tagId] || 0
  const values = Object.values(tagCounts.value)
  const maxCount = values.length > 0 ? Math.max(...values, 1) : 1

  const ratio = count / maxCount
  const minSize = 0.8
  const maxSize = 2.8
  const size = minSize + ratio * (maxSize - minSize)
  const opacity = 0.5 + ratio * 0.5

  return {
    fontSize: `${size}rem`,
    opacity: opacity,
    margin: `${10 * (1 - ratio)}px ${15 * ratio + 5}px`
  }
}

const getPopularTagStyle = (tagName: string) => {
  const views = tagViewsMap.value[tagName] || 0
  const ratio =
    maxViews.value === minViews.value
      ? 0.5
      : (views - minViews.value) / (maxViews.value - minViews.value)
  const minSize = 0.8
  const maxSize = 2.8
  const size = minSize + ratio * (maxSize - minSize)
  const opacity = 0.5 + ratio * 0.5

  return {
    fontSize: `${size}rem`,
    opacity: opacity,
    margin: `${10 * (1 - ratio)}px ${15 * ratio + 5}px`
  }
}

const openPanel = () => {
  isPanelOpen.value = true
}

const closePanel = () => {
  isPanelOpen.value = false
  resetForm()
}

const setEdit = (item: ITag) => {
  isEditing.value = true
  currentId.value = item.tag_id
  tagForm.tag_name = item.tag_name
  tagForm.content_ids = allContent.value
    .filter((c) => c.tags?.some((t: any) => t.tag_id === item.tag_id))
    .map((c) => c.content_id)
  openPanel()
}

const resetForm = () => {
  isEditing.value = false
  currentId.value = null
  tagForm.tag_name = ''
  tagForm.content_ids = []
}

const saveTag = async () => {
  try {
    if (isEditing.value && currentId.value) {
      await ApiService.request(`${Config.api.tagsDirect}/${currentId.value}`, {
        method: 'PUT',
        body: JSON.stringify(tagForm)
      })
    } else {
      await ApiService.createTag(tagForm)
    }
    closePanel()
    load()
    loadStatsAndTags()
  } catch (e: any) {
    alert(e.message)
  }
}

const deleteItem = async (item: ITag) => {
  if (confirm('Удалить этот тег?')) {
    try {
      await ApiService.deleteTag(item.tag_id)
      load()
      loadStatsAndTags()
    } catch (e: any) {
      alert(e.message)
    }
  }
}

const startResizing = () => {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', stopResizing)
  document.body.style.cursor = 'col-resize'
}

const stopResizing = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResizing)
  document.body.style.cursor = 'default'
}

const handleMouseMove = (e: MouseEvent) => {
  if (isResizing.value) {
    const container = document.querySelector('.tags-layout')
    if (container) {
      const containerRect = container.getBoundingClientRect()
      const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100
      if (newWidth > 20 && newWidth < 80) {
        cloudWidth.value = newWidth
      }
    }
  }
}

const startResizingVertical = () => {
  isResizingVertical.value = true
  document.addEventListener('mousemove', handleMouseMoveVertical)
  document.addEventListener('mouseup', stopResizingVertical)
  document.body.style.cursor = 'row-resize'
}

const stopResizingVertical = () => {
  isResizingVertical.value = false
  document.removeEventListener('mousemove', handleMouseMoveVertical)
  document.removeEventListener('mouseup', stopResizingVertical)
  document.body.style.cursor = 'default'
}

const handleMouseMoveVertical = (e: MouseEvent) => {
  if (isResizingVertical.value) {
    const container = document.querySelector('.cloud-wrapper')
    if (container) {
      const containerRect = container.getBoundingClientRect()
      const newHeight = ((e.clientY - containerRect.top) / containerRect.height) * 100
      if (newHeight > 20 && newHeight < 80) {
        topCloudHeight.value = newHeight
      }
    }
  }
}

onMounted(() => {
  load()
  loadStatsAndTags()
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResizing)
  document.removeEventListener('mousemove', handleMouseMoveVertical)
  document.removeEventListener('mouseup', stopResizingVertical)
})
</script>

<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0 fw-bold">Теги</h2>
    </div>

    <div class="tags-layout d-flex align-items-stretch">
      <div class="cloud-wrapper d-flex flex-column" :style="{ width: cloudWidth + '%' }">
        <div
          class="card shadow-sm border-0 d-flex flex-column"
          :style="{ height: topCloudHeight + '%' }"
        >
          <div class="card-header bg-white p-3 border-bottom-0 text-center flex-shrink-0">
            <h5 class="mb-0 fw-bold">Популярность по количеству</h5>
          </div>
          <div
            class="card-body d-flex flex-wrap align-items-center justify-content-center p-4 cloud-container flex-grow-1 overflow-auto"
          >
            <span
              v-for="tag in cloudTags"
              :key="tag.tag_id"
              class="tag-cloud-item"
              :style="getTagStyle(tag.tag_id)"
            >
              #{{ tag.tag_name }}
            </span>
            <div v-if="allTags.length === 0" class="text-muted small">Тегов пока нет</div>
          </div>
        </div>

        <div class="resizer-h" @mousedown="startResizingVertical"></div>

        <div
          class="card shadow-sm border-0 d-flex flex-column"
          :style="{ height: 100 - topCloudHeight + '%' }"
        >
          <div class="card-header bg-white p-3 border-bottom-0 text-center flex-shrink-0">
            <h5 class="mb-0 fw-bold">Популярность по просмотрам</h5>
          </div>
          <div
            class="card-body d-flex flex-wrap align-items-center justify-content-center p-4 cloud-container flex-grow-1 overflow-auto"
          >
            <span
              v-for="tag in cloudTags"
              :key="'views-' + tag.tag_id"
              class="tag-cloud-item popular-tag"
              :style="getPopularTagStyle(tag.tag_name)"
              :title="'Просмотры: ' + (tagViewsMap[tag.tag_name] || 0)"
            >
              #{{ tag.tag_name }}
            </span>
            <div v-if="allTags.length === 0" class="text-muted small">Нет данных по просмотрам</div>
          </div>
        </div>
      </div>

      <div class="resizer" @mousedown="startResizing"></div>

      <div class="right-wrapper d-flex flex-column" :style="{ width: 100 - cloudWidth + '%' }">
        <div class="card shadow-sm border-0 flex-grow-1 d-flex flex-column">
          <div class="card-header bg-white p-3 flex-shrink-0 d-flex gap-3">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"
                ><i class="bi bi-search text-muted"></i
              ></span>
              <input
                v-model="params.search"
                @input="load"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="Поиск по названию..."
              />
            </div>
            <button class="btn btn-primary fw-bold text-nowrap px-4" @click="openPanel()">Добавить тег</button>
          </div>

          <div class="card-body p-0 flex-grow-1 overflow-auto">
            <DataTable
              :columns="columns"
              :items="items"
              :has-actions="true"
              :current-page="params.page"
              :page-size="params.limit"
              :sort-config="{ key: params.sort, order: params.order }"
              @sort="handleSort"
              @edit="setEdit"
              @delete="deleteItem"
            >
              <template #cell-tag_name="{ item }">
                <span class="fw-medium">#{{ item.tag_name }}</span>
              </template>

              <template #cell-count="{ item }">
                <span class="badge bg-light text-dark border">
                  {{ item.count ?? 0 }}
                </span>
              </template>

              <template #cell-views_count="{ item }">
                <span class="badge bg-light text-success border">
                  {{ item.views_count ?? 0 }}
                </span>
              </template>

              <template #actions="{ item }">
                <button 
                  class="btn btn-sm btn-outline-primary me-2" 
                  @click="setEdit(item)"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-danger" 
                  :disabled="isEditing && currentId === item.tag_id"
                  @click="deleteItem(item)"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </template>
            </DataTable>
          </div>

          <div class="card-footer bg-white border-top-0 py-3 flex-shrink-0">
            <Pagination
              :current-page="params.page"
              :pages="pages"
              :total="total"
              @update:page="
                (p) => {
                  params.page = p
                  load()
                }
              "
            />
          </div>
        </div>
      </div>
    </div>

    <SidePanel
      :is-open="isPanelOpen"
      :title="isEditing ? 'Редактировать тег' : 'Добавить тег'"
      @close="closePanel"
    >
      <form @submit.prevent="saveTag" class="d-flex flex-column h-100">
        <div class="flex-grow-1">
          <div class="mb-3">
            <label class="form-label small fw-bold">Название тега</label>
            <input
              v-model="tagForm.tag_name"
              type="text"
              class="form-control"
              placeholder="Напр: боевик"
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label small fw-bold">Связанный контент</label>
            <CheckboxList
              v-model="tagForm.content_ids"
              :items="allContent"
              value-key="content_id"
              label-key="content_name"
              empty-text="Контент не найден"
              max-height="65vh"
            />
          </div>
        </div>
        
        <div class="d-flex gap-2 mt-4 pb-4">
          <button type="submit" class="btn btn-primary flex-grow-1 fw-bold">
            {{ isEditing ? 'Обновить' : 'Сохранить' }}
          </button>
          <button type="button" class="btn btn-light fw-bold" @click="closePanel">
            Отмена
          </button>
        </div>
      </form>
    </SidePanel>
  </div>
</template>

<style scoped>
.tags-layout {
  min-height: 750px;
  gap: 0;
  user-select: none;
}

.cloud-wrapper {
  min-width: 250px;
  position: relative;
}

.right-wrapper {
  min-width: 250px;
}

.cloud-container {
  align-content: center;
  text-align: center;
  background: radial-gradient(circle, rgba(255, 255, 255, 1) 0%, rgba(248, 249, 250, 0.4) 100%);
}

.tag-cloud-item {
  display: inline-block;
  transition: all 0.3s ease;
  cursor: default;
  color: #34495e;
  font-weight: 700;
  line-height: 1.2;
}

.tag-cloud-item:hover {
  transform: scale(1.1);
  color: var(--bs-primary);
  opacity: 1 !important;
}

.popular-tag {
  color: #198754;
}
.popular-tag:hover {
  color: #146c43;
}

.resizer {
  width: 16px;
  cursor: col-resize;
  background: transparent;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
}

.resizer::after {
  content: '';
  width: 3px;
  height: 40px;
  background: #dee2e6;
  border-radius: 3px;
}

.resizer:hover::after {
  background: #0d6efd;
  width: 5px;
}

.resizer-h {
  height: 16px;
  cursor: row-resize;
  background: transparent;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
}

.resizer-h::after {
  content: '';
  height: 3px;
  width: 40px;
  background: #dee2e6;
  border-radius: 3px;
}

.resizer-h:hover::after {
  background: #0d6efd;
  height: 5px;
}

.smallest {
  font-size: 0.75rem;
}
</style>