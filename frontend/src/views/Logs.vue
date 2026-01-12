<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">操作审计日志</h2>
      <p class="mt-1 text-sm text-muted-foreground">记录资产字段变更与关键操作。</p>
      <div class="mt-4 grid gap-3 md:grid-cols-4">
        <input class="input" placeholder="操作人" />
        <input class="input" placeholder="资产 ID / SN" />
        <select class="input">
          <option>全部动作</option>
          <option>IN</option>
          <option>OUT</option>
          <option>TRANSFER</option>
          <option>REPAIR</option>
          <option>DISCARD</option>
        </select>
        <Button>查询</Button>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>资产</th>
            <th>动作</th>
            <th>变更</th>
            <th>操作人</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>SN-AX93</td>
            <td>OUT</td>
            <td>status: 0 → 1</td>
            <td>管理员</td>
            <td>2026-01-12 10:05</td>
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
