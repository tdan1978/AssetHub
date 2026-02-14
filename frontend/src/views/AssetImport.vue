<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">批量导入资产</h2>
      <p class="mt-1 text-sm text-muted-foreground">按模板整理 Excel，系统会进行静态/业务校验并输出失败原因。</p>
      <div class="mt-4 flex flex-wrap gap-3">
        <Button variant="outline" @click="downloadTemplate">下载导入模板</Button>
        <label class="inline-flex items-center">
          <Input class="hidden" type="file" accept=".xlsx,.xls" @change="onFileChange" />
          <Button>上传 Excel</Button>
        </label>
      </div>
      <p v-if="message" class="mt-3 text-sm text-muted-foreground">{{ message }}</p>
      <div class="mt-4 text-xs text-muted-foreground">
        说明：SN 必须唯一，价值大于 5000 元需上传发票/合同附件。
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">最近导入记录</h3>
      <table class="table mt-3">
        <thead>
          <tr>
            <th>批次号</th>
            <th>导入人</th>
            <th>成功/失败</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>IMP-20260112-001</td>
            <td>系统管理员</td>
            <td>48 / 2</td>
            <td>2026-01-12 10:20</td>
            <td>
              <Button variant="outline" size="sm">下载失败原因</Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import api from "../api/client";
import { ref } from "vue";

const message = ref("");

const downloadTemplate = () => {
  const headers = ["sn", "asset_no", "name", "category", "purchase_at", "price", "warranty_at", "location", "attachment"];
  const csv = `${headers.join(",")}\n`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "asset_import_template.csv";
  link.click();
  URL.revokeObjectURL(url);
};

const onFileChange = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  message.value = "正在导入...";
  const form = new FormData();
  form.append("file", file);
  try {
    const response = await api.post("/assets/batch-import", form, { responseType: "blob" });
    const contentType = response.headers["content-type"] || "";
    if (contentType.includes("application/json")) {
      const text = await response.data.text();
      const data = JSON.parse(text);
      message.value = data.message || "导入完成";
    } else {
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = "import_errors.xlsx";
      link.click();
      URL.revokeObjectURL(url);
      message.value = "部分数据导入失败，请下载失败原因文件。";
    }
  } catch (err) {
    message.value = "导入失败，请检查文件格式或登录状态。";
  } finally {
    event.target.value = "";
  }
};
</script>

<style scoped></style>



