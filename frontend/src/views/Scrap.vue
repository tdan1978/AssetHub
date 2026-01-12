<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">报废管理</h2>
      <p class="mt-1 text-sm text-muted-foreground">在用资产需先退库再申请报废，审批通过后进入已报废。</p>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">发起报废申请</h3>
      <div class="mt-3 grid gap-2 md:grid-cols-3">
        <input class="input" placeholder="资产 ID / SN" />
        <input class="input" placeholder="报废原因" />
        <div class="flex items-center">
          <Button>提交申请</Button>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">报废申请列表</h3>
      <table class="table mt-3">
        <thead>
          <tr>
            <th>资产</th>
            <th>状态</th>
            <th>申请人</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>SN-AX93</td>
            <td>待报废</td>
            <td>李四</td>
            <td>2026-01-12</td>
            <td>
              <Button size="sm">审批通过</Button>
            </td>
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
