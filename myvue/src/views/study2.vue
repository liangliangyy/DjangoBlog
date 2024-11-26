<script setup>
import { reactive, computed,ref } from 'vue'

const author = reactive({
  name: 'John Doe',
  books: [
    
  ]
})

// a computed ref
const publishedBooksMessage = computed(() => {
  return author.books.length > 0 ? 'Yes' : 'No'
})
const now=computed(()=>Date.now())
//console.log(Date.now())
// const isActive = ref(true)
const hasError = ref(false)

const isActive = ref(true)
const error = ref(null)

const classObject = computed(() => ({
  active: isActive.value && !error.value,
  'text-danger': error.value && error.value.type === 'fatal'
}))
const activeColor = ref('red')
const fontSize = ref(30)
const awesome=ref(true)
const parentMessage = ref('Parent')
const items = ref([{ message: 'Foo' }, { message: 'Bar' }])
const myObject = reactive({
  title: 'How to do lists in Vue',
  author: 'Jane Doe',
  publishedAt: '2016-04-10'
})
function warn(message, event) {
  // 这里可以访问原生事件
  if (event) {
    event.preventDefault()
  }
  alert(message)
}

</script>

<template>
  <p>Has published books:</p>
  <span>{{ publishedBooksMessage }}</span>
  <div :class="{ active: isActive }">test</div>
  <span>{{now}}</span>
  <div
  class="static"
  :class="{ active: isActive, 'text-danger': hasError }"
>
</div>
<div :class="classObject"></div>
<div :style="{ color: activeColor, fontSize: fontSize + 'px' }">测试</div>

<button @click="awesome = !awesome">Toggle</button>

<h1 v-if="awesome">Vue is awesome!</h1>
<h1 v-else>Oh no 😢</h1>

<li v-for="(item, index) in items" :key="index">
  {{ parentMessage }} - {{ index }} - {{ item.message }}
</li>

<ul>
  <li v-for="value in myObject" :key="value">
    {{ value }}
  </li>
</ul>

<li v-for="(value, key,index) in myObject" :key="value">
  {{ key }}: {{ value }}:{{index}}
</li>


<!-- 使用特殊的 $event 变量 -->
<button @click="warn('Form cannot be submitted yet.', $event)">
  Submit
</button>

<!-- 使用内联箭头函数 -->
<button @click="(event) => warn('Form cannot be submitted yet.', event)">
  Submit
</button>
</template>