<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">系统设置</h2>
      <p class="mt-1 text-sm text-muted-foreground">系统安全、备份与全局参数配置。</p>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="card">
        <h3 class="text-sm font-semibold">安全与登录</h3>
        <div class="mt-3 grid gap-2">
          <Input placeholder="JWT 过期(小时)" value="24" />
          <Input placeholder="登录限流阈值" value="10" />
          <Button variant="outline">保存</Button>
        </div>
      </div>
      <div class="card">
        <h3 class="text-sm font-semibold">备份策略</h3>
        <div class="mt-3 grid gap-2">
          <Input placeholder="备份时间" value="03:00" />
          <Input placeholder="保留天数" value="30" />
          <Button variant="outline">立即备份</Button>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">系统公告</h3>
      <Textarea placeholder="维护通知或使用说明"></Textarea>
      <div class="mt-3">
        <Button variant="outline">发布公告</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
</script>

<style scoped></style>
