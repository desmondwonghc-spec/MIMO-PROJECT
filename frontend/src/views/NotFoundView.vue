<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <router-link to="/" class="btn">返回首页</router-link>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: #999;
}
.not-found h1 { font-size: 72px; margin: 0; color: #ddd; }
.btn {
  margin-top: 20px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
}
</style>
