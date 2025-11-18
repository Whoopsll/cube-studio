import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useResultDataStore = defineStore('resultData', () => {
  const resultData = ref(null)
  
  function setResultData(data) {
    resultData.value = data
  }
  
  function clearResultData() {
    resultData.value = null
  }
  
  return { resultData, setResultData, clearResultData }
})