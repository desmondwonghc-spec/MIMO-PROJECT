<template>
  <div class="resumes-page">
    <div class="page-toolbar">
      <h2>简历管理</h2>
      <button class="btn btn-primary">📤 上传简历</button>
    </div>
    <div class="empty-state">
      <p>📄 暂无简历，上传 PDF 或 Word 文件开始解析</p>
      <p class="hint">支持格式：.pdf, .docx</p>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.page-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-toolbar h2 { margin: 0; }
.btn { padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; border: none; }
.btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.empty-state { text-align: center; padding: 60px; background: #fff; border-radius: 8px; color: #999; }
.hint { font-size: 13px; color: #bbb; }
</style>
