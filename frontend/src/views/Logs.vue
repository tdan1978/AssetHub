<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">操作审计日志</h2>
      <p class="mt-1 text-sm text-muted-foreground">记录资产字段变更与关键操作。</p>
      <div class="mt-4 grid gap-4 md:grid-cols-4 items-end">
        <div class="form-field">
          <label class="form-label">操作人</label>
          <Input placeholder="操作人" />
        </div>
        <div class="form-field">
          <label class="form-label">资产 ID / SN</label>
          <Input placeholder="资产 ID / SN" />
        </div>
        <div class="form-field">
          <label class="form-label">动作</label>
          <Select v-model="action">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="全部动作" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部动作</SelectItem>
              <SelectItem value="IN">IN</SelectItem>
              <SelectItem value="OUT">OUT</SelectItem>
              <SelectItem value="TRANSFER">TRANSFER</SelectItem>
              <SelectItem value="REPAIR">REPAIR</SelectItem>
              <SelectItem value="DISCARD">DISCARD</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex items-end">
          <Button>查询</Button>
        </div>
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
import { ref } from "vue";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";

const action = ref("all");
</script>

<style scoped></style>



