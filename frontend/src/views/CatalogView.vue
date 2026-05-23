<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { ApiService } from '../services/api'
import type { IContent, IGenre, ITag, IAdvertising } from '../services/api'
import Pagination from '../components/Pagination.vue'

const movies = ref<IContent[]>([])
const genres = ref<IGenre[]>([])
const tags = ref<ITag[]>([])
const loading = ref(true)
const total = ref(0)
const totalPagesCount = ref(0)

const searchQuery = ref('')
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const params = reactive({
  page: 1,
  limit: 12,
  sort: 'content_id',
  order: 'desc',
  search: '',
  genre_ids: [] as number[],
  tag_ids: [] as number[]
})

const selectedMovie = ref<IContent | null>(null)
const currentProgress = ref(0)
const playerLoading = ref(false)
let tickInterval: ReturnType<typeof setInterval> | null = null

const showAd = ref(false)
const adData = ref<IAdvertising | null>(null)
const skipCountdown = ref(5)
let adInterval: ReturnType<typeof setInterval> | null = null

const pagesArray = computed(() => {
  const arr = []
  for (let i = 1; i <= totalPagesCount.value; i++) {
    arr.push(i)
  }
  return arr
})

const selectedTagsCount = computed(() => params.tag_ids.length)
const selectedGenresCount = computed(() => params.genre_ids.length)

const loadFilters = async () => {
  try {
    const [genresData, tagsData] = await Promise.all([ApiService.getGenres(), ApiService.getTags()])
    genres.value = genresData
    tags.value = tagsData
  } catch (e: any) {
    console.error(e.message)
  }
}

const loadCatalog = async () => {
  try {
    loading.value = true
    const response = await ApiService.getContent(params)
    movies.value = response.items
    total.value = response.total
    totalPagesCount.value = response.pages
  } catch (e: any) {
    console.error(e.message)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (newPage: number) => {
  params.page = newPage
  loadCatalog()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const resetFilters = () => {
  searchQuery.value = ''
  params.search = ''
  params.genre_ids = []
  params.tag_ids = []
  params.page = 1
  loadCatalog()
}

const saveProgress = async () => {
  const token = localStorage.getItem('token')
  if (selectedMovie.value && !showAd.value && token) {
    try {
      await ApiService.updateContentProgress(
        selectedMovie.value.content_id,
        Math.floor(currentProgress.value)
      )
    } catch (e) {
      console.error(e)
    }
  }
}

const handleMovieClick = async (movie: IContent) => {
  const token = localStorage.getItem('token')

  if (!token) {
    try {
      const ads = await ApiService.getContentAdvertising(movie.content_id)
      
      if (ads && ads.length > 0) {
        adData.value = ads[0] ?? null
        skipCountdown.value = 5
        showAd.value = true
        selectedMovie.value = movie
        document.body.style.overflow = 'hidden'
        
        adInterval = setInterval(() => {
          if (skipCountdown.value > 0) {
            skipCountdown.value--
          } else {
            if (adInterval) clearInterval(adInterval)
          }
        }, 1000)
        return
      }
    } catch (e) {
      console.error('Ошибка загрузки рекламы:', e)
    }
  }

  selectedMovie.value = movie
  startPlayer(movie)
}

const skipAd = () => {
  if (adInterval) clearInterval(adInterval)
  if (selectedMovie.value) {
    startPlayer(selectedMovie.value)
  }
}

const startPlayer = async (movie: IContent) => {
  showAd.value = false
  adData.value = null
  currentProgress.value = 0
  playerLoading.value = true
  document.body.style.overflow = 'hidden'

  const token = localStorage.getItem('token')

  if (token) {
    try {
      const response = await ApiService.getContentProgress(movie.content_id)
      currentProgress.value = response.progress || 0
    } catch (e) {
      currentProgress.value = 0
    }
  }

  playerLoading.value = false

  if (token) {
    tickInterval = setInterval(saveProgress, 20000)
  }
}

const closePlayer = async () => {
  if (adInterval) clearInterval(adInterval)
  if (tickInterval) clearInterval(tickInterval)
  tickInterval = null
  
  if (!showAd.value) {
    await saveProgress()
  }
  
  selectedMovie.value = null
  showAd.value = false
  adData.value = null
  currentProgress.value = 0
  document.body.style.overflow = ''
}

const handleUnload = () => {
  if (selectedMovie.value && !showAd.value) {
    saveProgress()
  }
}

watch(searchQuery, (newVal) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    params.search = newVal
    params.page = 1
    loadCatalog()
  }, 500)
})

watch(
  () => params.genre_ids,
  () => {
    params.page = 1
    loadCatalog()
  },
  { deep: true }
)

watch(
  () => params.tag_ids,
  () => {
    params.page = 1
    loadCatalog()
  },
  { deep: true }
)

onMounted(() => {
  loadFilters()
  loadCatalog()
  window.addEventListener('beforeunload', handleUnload)
})

onUnmounted(() => {
  if (tickInterval) clearInterval(tickInterval)
  if (adInterval) clearInterval(adInterval)
  window.removeEventListener('beforeunload', handleUnload)
})
</script>

<template>
  <div class="container-fluid">
    <div
      class="text-center py-5 rounded-4 mb-5 shadow"
      style="background-color: var(--sidebar-bg); color: var(--sidebar-text-light)"
    >
      <h1 class="display-4 fw-bold">MishlenKino</h1>
      <p class="lead">Ваш персональный кинозал с лучшим контентом.</p>
    </div>

    <div
      class="card border-0 shadow-sm mb-4 p-3"
      style="background-color: var(--card-bg); border-radius: 16px"
    >
      <div class="row g-3 align-items-center">
        <div class="col-12 col-lg-4">
          <div class="input-group">
            <span class="input-group-text border-0 bg-transparent" style="color: var(--text-muted)">
              <i class="bi bi-search"></i>
            </span>
            <input
              v-model="searchQuery"
              type="text"
              class="form-control border-0 bg-transparent ps-0"
              placeholder="Найти фильм или сериал..."
              style="color: var(--text-darker)"
            />
          </div>
        </div>

        <div class="col-12 col-md-4 col-lg-3">
          <div class="dropdown w-100">
            <button
              class="btn w-100 text-start dropdown-toggle d-flex justify-content-between align-items-center"
              type="button"
              data-bs-toggle="dropdown"
              data-bs-auto-close="outside"
              style="
                background-color: var(--body-bg);
                color: var(--text-darker);
                border-radius: 10px;
                border: none;
              "
            >
              <span>{{
                selectedGenresCount > 0 ? `Жанры (${selectedGenresCount})` : 'Выбрать жанры'
              }}</span>
            </button>
            <div
              class="dropdown-menu p-3 shadow-lg border-0 mt-2"
              style="width: 280px; max-height: 350px; overflow-y: auto; border-radius: 12px"
            >
              <div
                v-for="genre in genres"
                :key="genre.genre_id"
                class="form-check mb-2 custom-check"
              >
                <input
                  class="form-check-input"
                  type="checkbox"
                  :id="'genre-' + genre.genre_id"
                  :value="genre.genre_id"
                  v-model="params.genre_ids"
                />
                <label class="form-check-label w-100" :for="'genre-' + genre.genre_id">
                  {{ genre.genre_name }}
                </label>
              </div>
              <div v-if="genres.length === 0" class="text-center py-2 text-muted small">
                Жанры не найдены
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-4 col-lg-3">
          <div class="dropdown w-100">
            <button
              class="btn w-100 text-start dropdown-toggle d-flex justify-content-between align-items-center"
              type="button"
              data-bs-toggle="dropdown"
              data-bs-auto-close="outside"
              style="
                background-color: var(--body-bg);
                color: var(--text-darker);
                border-radius: 10px;
                border: none;
              "
            >
              <span>{{
                selectedTagsCount > 0 ? `Теги (${selectedTagsCount})` : 'Выбрать теги'
              }}</span>
            </button>
            <div
              class="dropdown-menu p-3 shadow-lg border-0 mt-2"
              style="width: 280px; max-height: 350px; overflow-y: auto; border-radius: 12px"
            >
              <div v-for="tag in tags" :key="tag.tag_id" class="form-check mb-2 custom-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  :id="'tag-' + tag.tag_id"
                  :value="tag.tag_id"
                  v-model="params.tag_ids"
                />
                <label class="form-check-label w-100" :for="'tag-' + tag.tag_id">
                  {{ tag.tag_name }}
                </label>
              </div>
              <div v-if="tags.length === 0" class="text-center py-2 text-muted small">
                Теги не найдены
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-4 col-lg-2">
          <button
            @click="resetFilters"
            class="btn w-100 fw-bold"
            style="
              background-color: var(--sidebar-bg);
              color: var(--sidebar-text-light);
              border-radius: 10px;
            "
          >
            Сбросить
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-grow" style="color: var(--sidebar-primary)" role="status"></div>
    </div>

    <div v-else>
      <div class="row g-4 mb-5">
        <div v-for="movie in movies" :key="movie.content_id" class="col-md-6 col-lg-4 col-xl-3">
          <div
            class="card h-100 border-0 shadow-sm movie-card"
            style="background-color: var(--card-bg)"
          >
            <div class="card-body d-flex flex-column p-4">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <span
                  class="badge px-2 py-1"
                  style="
                    background-color: var(--warning-color);
                    color: var(--text-darker);
                    font-size: 0.75rem;
                  "
                >
                  {{ movie.content_type }}
                </span>
                <span class="small text-muted fw-bold">{{ movie.content_duration }}</span>
              </div>

              <h5 class="card-title mb-1 fw-bold fs-5" style="color: var(--text-darker)">
                {{ movie.content_name }}
              </h5>

              <div class="mb-3">
                <p class="small mb-0" style="color: var(--sidebar-primary); font-weight: 600">
                  {{ movie.genres.map((g) => g.genre_name).join(', ') || 'Без жанра' }}
                </p>
              </div>

              <div class="mb-3 d-flex flex-wrap gap-1">
                <span
                  v-for="tag in movie.tags"
                  :key="tag.tag_id"
                  class="text-muted"
                  style="font-size: 0.8rem"
                >
                  #{{ tag.tag_name }}
                </span>
              </div>

              <p
                class="small text-truncate-custom flex-grow-1"
                style="color: var(--text-muted); line-height: 1.5; font-size: 0.9rem"
              >
                {{ movie.content_discription || 'Нет описания для данного контента.' }}
              </p>

              <div class="mt-auto pt-3 border-top">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <small class="text-muted"
                    >Премьера: {{ new Date(movie.content_publish_date).getFullYear() }}</small
                  >
                </div>
                <button
                  @click="handleMovieClick(movie)"
                  class="btn w-100 py-2 fw-bold action-btn"
                  style="background-color: var(--sidebar-primary); color: #fff; border-radius: 8px"
                >
                  Смотреть
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="movies.length === 0" class="col-12 text-center py-5">
          <div class="p-5">
            <h4 style="color: var(--text-darker)">Контент не найден</h4>
            <p class="text-muted">Попробуйте изменить фильтры или поисковый запрос.</p>
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-center pb-5" v-if="totalPagesCount > 1">
        <Pagination
          :current-page="params.page"
          :pages="pagesArray"
          :total="total"
          @update:page="handlePageChange"
        />
      </div>
    </div>

    <div v-if="selectedMovie" class="player-overlay" @click.self="closePlayer">
      <div class="player-modal shadow-lg">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h4 class="mb-0 text-white fw-bold">{{ showAd ? 'Реклама' : selectedMovie.content_name }}</h4>
            <small class="text-white-50" v-if="!showAd"
              >{{ selectedMovie.content_type }} • {{ selectedMovie.content_duration }}</small
            >
          </div>
          <button
            @click="closePlayer"
            class="btn btn-link text-white text-decoration-none fs-4 p-0"
          >
            &times;
          </button>
        </div>

        <div v-if="showAd" class="video-placeholder rounded-3 mb-4 d-flex flex-column align-items-center justify-content-center p-4 text-center position-relative">
          <div class="position-absolute top-0 start-0 m-3 badge bg-warning text-dark px-3 py-2 fs-6">Реклама</div>
          <i class="bi bi-megaphone-fill text-warning mb-3" style="font-size: 3rem;"></i>
          <h2 class="text-white fw-bold mb-2">{{ adData?.advertising_name || 'Рекламная пауза' }}</h2>
          <p class="text-white-50 fs-5 mb-4">Спонсор показа: {{ adData?.advertising_owner || 'Неизвестно' }}</p>
          <button 
            class="btn btn-light rounded-pill px-5 py-2 fw-bold" 
            :disabled="skipCountdown > 0" 
            @click="skipAd"
          >
            <span v-if="skipCountdown > 0">Пропустить через {{ skipCountdown }} сек</span>
            <span v-else>Пропустить рекламу <i class="bi bi-skip-forward-fill ms-1"></i></span>
          </button>
        </div>

        <div v-else class="video-placeholder rounded-3 mb-4 d-flex align-items-center justify-content-center">
          <div v-if="playerLoading" class="spinner-border text-light" role="status"></div>
          <div v-else class="text-center text-white-50">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="64"
              height="64"
              fill="currentColor"
              class="bi bi-play-circle mb-2"
              viewBox="0 0 16 16"
            >
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" />
              <path
                d="M6.271 5.055a.5.5 0 0 1 .52.038l3.5 2.5a.5.5 0 0 1 0 .814l-3.5 2.5A.5.5 0 0 1 6 10.5v-5a.5.5 0 0 1 .271-.445"
              />
            </svg>
            <p class="mb-0">Имитация видеоплеера</p>
          </div>
        </div>

        <div v-if="!showAd" class="d-flex align-items-center gap-3">
          <span class="text-white-50 small">0%</span>
          <input
            type="range"
            class="form-range flex-grow-1 custom-range"
            min="0"
            max="100"
            v-model="currentProgress"
            :disabled="playerLoading"
          />
          <span class="text-white fw-bold" style="min-width: 45px; text-align: right"
            >{{ currentProgress }}%</span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-card {
  transition:
    transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275),
    box-shadow 0.3s ease;
  border-radius: 20px !important;
}
.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.12) !important;
}
.action-btn {
  transition: all 0.2s ease;
  border: none;
}
.action-btn:hover {
  opacity: 0.9;
  transform: scale(1.02);
}
.custom-check .form-check-input:checked {
  background-color: var(--sidebar-primary);
  border-color: var(--sidebar-primary);
}
.custom-check .form-check-label {
  cursor: pointer;
  transition: color 0.2s;
}
.custom-check:hover .form-check-label {
  color: var(--sidebar-primary);
}
.text-truncate-custom {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.dropdown-toggle::after {
  margin-left: auto;
}

.player-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  backdrop-filter: blur(5px);
}

.player-modal {
  background-color: #1a1a1a;
  width: 100%;
  max-width: 900px;
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid #333;
}

.video-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: #000;
  border: 1px solid #333;
}

.custom-range::-webkit-slider-thumb {
  background: var(--sidebar-primary);
}
.custom-range::-moz-range-thumb {
  background: var(--sidebar-primary);
}
.custom-range::-ms-thumb {
  background: var(--sidebar-primary);
}
</style>