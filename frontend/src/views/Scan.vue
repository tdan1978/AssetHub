<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">扫码工具</h2>
      <p class="mt-1 text-sm text-muted-foreground">移动端扫码后展示资产信息，支持报修与交还申请。</p>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="card">
        <h3 class="text-sm font-semibold">员工视图</h3>
        <div class="mt-3 space-y-2 text-sm">
          <div>资产名称：MacBook Pro 14</div>
          <div>规格：M2 Pro / 16GB / 1TB</div>
          <div>维保期：2027-06-30</div>
        </div>
        <div class="mt-4 flex gap-2">
          <Button>报修申请</Button>
          <Button variant="outline">交还申请</Button>
        </div>
      </div>

      <div class="card">
        <h3 class="text-sm font-semibold">管理员视图</h3>
        <div class="mt-3 space-y-2 text-sm">
          <div>资产编号：IT-20260112-0001</div>
          <div>当前状态：在用</div>
          <div>位置：A区-机柜 03</div>
        </div>
        <div class="mt-4 flex gap-2">
          <Button>状态变更</Button>
          <Button variant="outline">位置移动</Button>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">扫码记录</h3>
      <table class="table mt-3">
        <thead>
          <tr>
            <th>资产</th>
            <th>扫描人</th>
            <th>结果</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>SN-AX93</td>
            <td>王五</td>
            <td>正常</td>
            <td>2026-01-12 10:40</td>
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



