<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">财务报表与审计导出</h2>
      <p class="mt-1 text-sm text-muted-foreground">资产价值、折旧统计与合同附件导出。</p>
      <div class="mt-4 flex flex-wrap gap-3">
        <Button>导出资产清单</Button>
        <Button variant="secondary">导出折旧报表</Button>
        <Button variant="outline">导出审计报表</Button>
      </div>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <div class="card">
        <div class="text-xs text-muted-foreground">资产原值</div>
        <div class="mt-2 text-2xl font-semibold">¥ 1,280,000</div>
      </div>
      <div class="card">
        <div class="text-xs text-muted-foreground">累计折旧</div>
        <div class="mt-2 text-2xl font-semibold">¥ 420,000</div>
      </div>
      <div class="card">
        <div class="text-xs text-muted-foreground">净值</div>
        <div class="mt-2 text-2xl font-semibold">¥ 860,000</div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">重点资产列表</h3>
      <table class="table mt-3">
        <thead>
          <tr>
            <th>资产</th>
            <th>金额</th>
            <th>部门</th>
            <th>附件</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>服务器 DELL R750</td>
            <td>¥ 120,000</td>
            <td>数据中心</td>
            <td>
              <Button size="sm" variant="secondary">查看</Button>
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



