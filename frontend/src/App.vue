<template>
  <RouterView />
  <Toast position="bottom-right" />
  <PrimeConfirmDialog />
</template>

<script setup>
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import PrimeConfirmDialog from 'primevue/confirmdialog'
</script>
