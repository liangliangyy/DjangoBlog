<template>
  <nav>
    <router-link to="/">Home</router-link> |
    <router-link to="/about">About</router-link>
  </nav>
  <router-view/>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #FFC68C;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #D3C1AF;
}

nav a.router-link-exact-active {
  color: #BD467C;
}
</style>
