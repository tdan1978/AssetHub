<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">角色权限</h2>
      <p class="mt-1 text-sm text-muted-foreground">按角色分配访问权限（当前仅展示）。</p>
      <div class="mt-3">
        <Button variant="outline" disabled>新增角色</Button>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>角色</th>
            <th>权限摘要</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>超级管理员</td>
            <td>系统配置、角色分配、操作审计</td>
          </tr>
          <tr>
            <td>资产管理员</td>
            <td>资产入库、领用/退库、盘点发起</td>
          </tr>
          <tr>
            <td>财务审计</td>
            <td>价值查询、折旧、审计导出</td>
          </tr>
          <tr>
            <td>普通员工</td>
            <td>个人资产、报修申请</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { Button } from "../components/ui/button";
</script>

<style scoped></style>
