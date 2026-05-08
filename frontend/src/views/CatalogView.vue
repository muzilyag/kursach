<script setup lang="ts">
import { ref } from 'vue'

const mockMovies = [
  { id: 1, title: 'Интерстеллар', genre: 'Фантастика', rating: 8.6, img: 'https://placehold.co/400x600?text=Interstellar' },
  { id: 2, title: 'Начало', genre: 'Боевик', rating: 8.8, img: 'https://placehold.co/400x600?text=Inception' },
  { id: 3, title: 'Дюна', genre: 'Приключения', rating: 8.1, img: 'https://placehold.co/400x600?text=Dune' },
  { id: 4, title: 'Темный рыцарь', genre: 'Криминал', rating: 9.0, img: 'https://placehold.co/400x600?text=Batman' }
]
</script>

<template>
  <div class="container-fluid">
    <div class="text-center py-5 rounded-4 mb-5 shadow" style="background-color: var(--sidebar-bg); color: var(--sidebar-text-light);">
      <h1 class="display-4 fw-bold">MishlenKino</h1>
      <p class="lead">Смотрите лучшие фильмы и сериалы в высоком качестве.</p>
    </div>

    <h3 class="mb-4" style="color: var(--text-darker);">Каталог контента</h3>
    <div class="row g-4">
      <div v-for="movie in mockMovies" :key="movie.id" class="col-md-3">
        <div class="card h-100 border-0 shadow-sm movie-card" style="background-color: var(--card-bg);">
          <img :src="movie.img" class="card-img-top rounded-top" alt="Poster">
          <div class="card-body">
            <span class="badge mb-2" style="background-color: var(--warning-color); color: var(--text-darker);">⭐ {{ movie.rating }}</span>
            <h5 class="card-title mb-1" style="color: var(--text-darker);">{{ movie.title }}</h5>
            <p class="small" style="color: var(--text-muted);">{{ movie.genre }}</p>
            <button class="btn btn-sm w-100" style="border: 1px solid var(--sidebar-primary); color: var(--sidebar-primary);">Смотреть</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-card { transition: transform 0.2s; cursor: pointer; }
.movie-card:hover { transform: translateY(-10px); }
</style>