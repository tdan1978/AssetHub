<template>
  <div class="dashboard-page">
    <div class="hero-panel mb-2 flex flex-col gap-3 p-5 md:flex-row md:items-center md:justify-between">
      <div>
        <p class="hero-eyebrow">Dashboard</p>
        <h1 class="hero-title">资产看板</h1>
        <p class="hero-desc">支持模板化配置图表样式、尺寸和数据源参数</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <span class="hero-chip">总资产 {{ data.total || 0 }}</span>
        <Button variant="outline" @click="refresh">刷新数据</Button>
        <Button v-if="canEditDashboard" @click="openDesigner">编辑看板</Button>
      </div>
    </div>

    <div class="kpi-grid grid gap-4 md:grid-cols-5">
      <div
        v-for="widget in kpiWidgets"
        :key="widget.widget_key"
        class="card kpi-card"
        :class="cardVariantClass(widget.style_config?.variant)"
        :style="widgetCardStyle(widget, kpiGridStyle(widget))"
      >
        <div class="label">{{ widget.title }}</div>
        <div class="value">{{ formatKpiValue(widget.metric_key) }}</div>
      </div>
    </div>

    <div v-if="chartWidgets.length" class="chart-grid mt-6 grid gap-4 lg:grid-cols-3">
      <div
        v-for="widget in chartWidgets"
        :key="widget.widget_key"
        class="card chart-card"
        :class="[cardVariantClass(widget.style_config?.variant), densityClass(widget.style_config?.density)]"
        :style="widgetCardStyle(widget, chartGridStyle(widget))"
      >
        <div class="chart-title">{{ widget.title }}</div>

        <ChartContainer v-if="widget.metric_key === 'chart_asset_status' && isDonutType(widget)" :config="statusChartConfig" class="chart-body chart-split">
          <div class="donut-wrap">
            <VisSingleContainer :data="assetStatusSeries(widget)" :height="chartHeight(widget)" :width="chartHeight(widget)">
              <ChartTooltip :triggers="{ [VisDonutSelectors.segment]: donutTooltip }" :followCursor="true" />
              <VisDonut
                :value="(d) => d.value"
                :color="(d) => chartColor(d.key)"
                :radius="Math.max(52, Math.round(chartHeight(widget) * 0.34))"
                :arcWidth="16"
                :showEmptySegments="false"
                :centralLabel="String(data.total || 0)"
                :centralSubLabel="'总资产'"
                :centralLabelOffsetY="8"
                :label="() => ''"
              />
            </VisSingleContainer>
          </div>
        </ChartContainer>
        <ChartContainer v-else-if="widget.metric_key === 'chart_asset_status'" :config="statusChartConfig" class="chart-body chart-shell">
          <VisXYContainer :data="assetStatusBarData(widget)" :height="chartHeight(widget)">
            <ChartTooltip :triggers="{ [VisGroupedBarSelectors.bar]: devLangTooltip }" :followCursor="true" />
            <VisGroupedBar :x="(d) => d.index" :y="(d) => d.value" :color="(d) => chartColor(d.key)" :roundedCorners="6" :barPadding="0.2" />
            <VisAxis type="x" :x="(d) => d.index" :tickFormat="assetStatusLabel(widget)" :tickTextColor="'var(--muted-foreground)'" :gridLine="false" :domainLine="false" :tickLine="false" />
            <VisAxis type="y" :y="(d) => d.value" :numTicks="4" :tickTextColor="'var(--muted-foreground)'" :gridLine="true" :domainLine="false" :tickLine="false" />
          </VisXYContainer>
        </ChartContainer>

        <ChartContainer v-else-if="widget.metric_key === 'chart_asset_trend' && chartType(widget) === 'line'" :config="trendChartConfig" class="chart-body chart-shell">
          <VisXYContainer :data="monthlyData" :height="chartHeight(widget)">
            <ChartTooltip :followCursor="true" />
            <ChartCrosshair :template="trendTooltip" :color="chartColor('assets')" />
            <VisArea :x="(d) => d.index" :y="(d) => d.count" :color="chartColor('assets')" :opacity="0.12" curveType="monotoneX" />
            <VisLine :x="(d) => d.index" :y="(d) => d.count" :color="chartColor('assets')" :lineWidth="2" curveType="monotoneX" />
            <VisAxis type="x" :x="(d) => d.index" :tickFormat="formatMonth" :numTicks="6" :tickTextColor="'var(--muted-foreground)'" :gridLine="false" :domainLine="false" :tickLine="false" />
            <VisAxis type="y" :y="(d) => d.count" :numTicks="4" :tickTextColor="'var(--muted-foreground)'" :gridLine="true" :domainLine="false" :tickLine="false" />
          </VisXYContainer>
        </ChartContainer>
        <ChartContainer v-else-if="widget.metric_key === 'chart_asset_trend'" :config="trendChartConfig" class="chart-body chart-shell">
          <VisXYContainer :data="monthlyData" :height="chartHeight(widget)">
            <ChartTooltip :triggers="{ [VisGroupedBarSelectors.bar]: trendBarTooltip }" :followCursor="true" />
            <VisGroupedBar :x="(d) => d.index" :y="(d) => d.count" color="var(--chart-3)" :roundedCorners="6" :barPadding="0.2" />
            <VisAxis type="x" :x="(d) => d.index" :tickFormat="formatMonth" :numTicks="6" :tickTextColor="'var(--muted-foreground)'" :gridLine="false" :domainLine="false" :tickLine="false" />
            <VisAxis type="y" :y="(d) => d.count" :numTicks="4" :tickTextColor="'var(--muted-foreground)'" :gridLine="true" :domainLine="false" :tickLine="false" />
          </VisXYContainer>
        </ChartContainer>

        <ChartContainer v-else-if="widget.metric_key === 'chart_license_expiry'" :config="licenseChartConfig" class="chart-body chart-shell">
          <VisXYContainer :data="licenseData" :height="chartHeight(widget)">
            <ChartTooltip :triggers="{ [VisGroupedBarSelectors.bar]: licenseTooltip }" :followCursor="true" />
            <VisGroupedBar :x="(d) => d.index" :y="(d) => d.value" color="var(--chart-3)" :roundedCorners="6" :barPadding="0.2" />
            <VisAxis type="x" :x="(d) => d.index" :tickFormat="formatLicenseLabel" :tickTextColor="'var(--muted-foreground)'" :gridLine="false" :domainLine="false" :tickLine="false" />
            <VisAxis type="y" :y="(d) => d.value" :numTicks="4" :tickTextColor="'var(--muted-foreground)'" :gridLine="true" :domainLine="false" :tickLine="false" />
          </VisXYContainer>
        </ChartContainer>
        <ChartContainer v-else-if="widget.metric_key === 'chart_system_dev_lang' && isDonutType(widget)" :config="devLangChartConfig(widget)" class="chart-body chart-split">
          <div class="donut-wrap">
            <VisSingleContainer :data="devLangData(widget)" :height="chartHeight(widget)" :width="chartHeight(widget)">
              <ChartTooltip :triggers="{ [VisDonutSelectors.segment]: devLangDonutTooltip }" :followCursor="true" />
              <VisDonut
                :value="(d) => d.value"
                :color="(d) => chartColor(d.key)"
                :radius="Math.max(52, Math.round(chartHeight(widget) * 0.34))"
                :arcWidth="16"
                :showEmptySegments="false"
                :centralLabel="String(devLangTotal(widget))"
                :centralSubLabel="'开发语言'"
                :centralLabelOffsetY="8"
                :label="() => ''"
              />
            </VisSingleContainer>
          </div>
        </ChartContainer>

        <ChartContainer v-else-if="widget.metric_key === 'chart_system_dev_lang' && !isDonutType(widget)" :config="devLangChartConfig(widget)" class="chart-body chart-shell">
          <VisXYContainer :data="devLangData(widget)" :height="chartHeight(widget)">
            <ChartTooltip :triggers="{ [VisGroupedBarSelectors.bar]: devLangTooltip }" :followCursor="true" />
            <VisGroupedBar :x="(d) => d.index" :y="(d) => d.value" :color="(d) => chartColor(d.key)" :roundedCorners="6" :barPadding="0.2" />
            <VisAxis type="x" :x="(d) => d.index" :tickFormat="formatDevLangLabel(widget)" :tickTextColor="'var(--muted-foreground)'" :gridLine="false" :domainLine="false" :tickLine="false" />
            <VisAxis type="y" :y="(d) => d.value" :numTicks="4" :tickTextColor="'var(--muted-foreground)'" :gridLine="true" :domainLine="false" :tickLine="false" />
          </VisXYContainer>
        </ChartContainer>
        <ChartContainer v-else-if="widget.metric_key === 'chart_system_status' && !isDonutType(widget)" :config="systemStatusConfig(widget)" class="chart-body chart-shell">
          <VisXYContainer :data="systemStatusData(widget)" :height="chartHeight(widget)">
            <ChartTooltip :triggers="{ [VisGroupedBarSelectors.bar]: systemStatusBarTooltip }" :followCursor="true" />
            <VisGroupedBar :x="(d) => d.index" :y="(d) => d.value" :color="(d) => chartColor(d.key)" :roundedCorners="6" :barPadding="0.2" />
            <VisAxis type="x" :x="(d) => d.index" :tickFormat="systemStatusLabel(widget)" :tickTextColor="'var(--muted-foreground)'" :gridLine="false" :domainLine="false" :tickLine="false" />
            <VisAxis type="y" :y="(d) => d.value" :numTicks="4" :tickTextColor="'var(--muted-foreground)'" :gridLine="true" :domainLine="false" :tickLine="false" />
          </VisXYContainer>
        </ChartContainer>

        <ChartContainer v-else-if="widget.metric_key === 'chart_system_status' && isDonutType(widget)" :config="systemStatusConfig(widget)" class="chart-body chart-split">
          <div class="donut-wrap">
            <VisSingleContainer :data="systemStatusData(widget)" :height="chartHeight(widget)" :width="chartHeight(widget)">
              <ChartTooltip :triggers="{ [VisDonutSelectors.segment]: systemStatusTooltip }" :followCursor="true" />
              <VisDonut
                :value="(d) => d.value"
                :color="(d) => chartColor(d.key)"
                :radius="Math.max(52, Math.round(chartHeight(widget) * 0.34))"
                :arcWidth="16"
                :showEmptySegments="false"
                :centralLabel="String(systemStatusTotal(widget))"
                :centralSubLabel="'系统资产'"
                :centralLabelOffsetY="8"
                :label="() => ''"
              />
            </VisSingleContainer>
          </div>
        </ChartContainer>
      </div>
    </div>

    <Dialog v-model:open="designerOpen">
      <DialogContent class="w-[96vw] max-w-[1200px]">
        <DialogHeader>
          <DialogTitle>看板编辑</DialogTitle>
          <DialogDescription>可配置标题、样式、大小和数据源参数（topN）</DialogDescription>
        </DialogHeader>

        <div class="max-h-[68vh] overflow-auto rounded-md border">
          <table class="w-full text-sm">
            <thead class="bg-muted/50">
              <tr>
                <th class="px-2 py-2 text-left">启用</th>
                <th class="px-2 py-2 text-left">组件</th>
                <th class="px-2 py-2 text-left">标题</th>
                <th class="px-2 py-2 text-left">指标</th>
                <th class="px-2 py-2 text-left">宽度</th>
                <th class="px-2 py-2 text-left">图形</th>
                <th class="px-2 py-2 text-left">密度</th>
                <th class="px-2 py-2 text-left">样式</th>
                <th class="px-2 py-2 text-left">topN</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in editingWidgets" :key="item.widget_key" class="border-t align-top">
                <td class="px-2 py-2"><input v-model="item.is_active" type="checkbox" /></td>
                <td class="px-2 py-2">{{ item.widget_key }}</td>
                <td class="px-2 py-2"><Input v-model="item.title" class="h-8" /></td>
                <td class="px-2 py-2">
                  <select v-model="item.metric_key" class="h-8 rounded-md border bg-background px-2">
                    <option v-for="opt in metricOptionsFor(item.widget_type)" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </td>
                <td class="px-2 py-2">
                  <select v-model.number="item.col_span" class="h-8 rounded-md border bg-background px-2">
                    <option :value="1">1</option>
                    <option :value="2">2</option>
                    <option :value="3">3</option>
                  </select>
                </td>
                <td class="px-2 py-2">
                  <select v-if="item.widget_type === 'chart'" v-model="item.style_config.chart_type" class="h-8 rounded-md border bg-background px-2">
                    <option v-for="opt in chartTypeOptionsForMetric(item.metric_key)" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                  <span v-else class="text-muted-foreground">-</span>
                </td>
                <td class="px-2 py-2">
                  <select v-model="item.style_config.density" class="h-8 rounded-md border bg-background px-2">
                    <option value="compact">紧凑</option>
                    <option value="normal">常规</option>
                  </select>
                </td>
                <td class="px-2 py-2">
                  <select v-model="item.style_config.variant" class="h-8 rounded-md border bg-background px-2">
                    <option value="default">默认</option>
                    <option value="soft">柔和</option>
                    <option value="outline">描边</option>
                  </select>
                </td>
                <td class="px-2 py-2">
                  <Input v-model.number="item.data_source_config.top_n" class="h-8 w-20" type="number" min="1" max="50" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <DialogFooter class="gap-2">
          <Button variant="outline" @click="designerOpen = false">关闭</Button>
          <Button variant="outline" :disabled="saving" @click="saveDashboardDraft">保存草稿</Button>
          <Button v-if="canPublishDashboard" :disabled="saving" @click="publishDashboard">发布</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { toast } from "vue-sonner";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartCrosshair, componentToString } from "../components/ui/chart";
import { VisDonut, VisSingleContainer, VisXYContainer, VisLine, VisArea, VisAxis, VisGroupedBar, VisGroupedBarSelectors, VisDonutSelectors } from "@unovis/vue";

const data = ref({
  total: 0,
  in_use_rate: 0,
  repairing: 0,
  pending_scrap: 0,
  license_expire_warn: 0,
  status_counts: { idle: 0, in_use: 0, repairing: 0, pending_scrap: 0, scrapped: 0 },
  license_expire_buckets: { d30: 0, d60: 0, d90: 0 },
  monthly_assets: [],
  system_status_counts: [],
  system_dev_lang_counts: [],
});

const defaultWidgets = [
  { widget_key: "kpi_total_assets", title: "总资产", widget_type: "kpi", metric_key: "kpi_total_assets", col_span: 1, sort_order: 10, style_config: { variant: "default", density: "compact" }, data_source_config: {}, is_active: true },
  { widget_key: "kpi_in_use_rate", title: "在用率", widget_type: "kpi", metric_key: "kpi_in_use_rate", col_span: 1, sort_order: 20, style_config: { variant: "default", density: "compact" }, data_source_config: {}, is_active: true },
  { widget_key: "kpi_repairing", title: "维修中", widget_type: "kpi", metric_key: "kpi_repairing", col_span: 1, sort_order: 30, style_config: { variant: "default", density: "compact" }, data_source_config: {}, is_active: true },
  { widget_key: "kpi_pending_scrap", title: "待报废", widget_type: "kpi", metric_key: "kpi_pending_scrap", col_span: 1, sort_order: 40, style_config: { variant: "default", density: "compact" }, data_source_config: {}, is_active: true },
  { widget_key: "kpi_license_warn", title: "授权到期预警", widget_type: "kpi", metric_key: "kpi_license_warn", col_span: 1, sort_order: 50, style_config: { variant: "default", density: "compact" }, data_source_config: {}, is_active: true },
  { widget_key: "chart_asset_status", title: "资产状态分布", widget_type: "chart", metric_key: "chart_asset_status", col_span: 1, sort_order: 100, style_config: { variant: "default", density: "compact", chart_type: "donut" }, data_source_config: {}, is_active: true },
  { widget_key: "chart_asset_trend", title: "近12个月新增趋势", widget_type: "chart", metric_key: "chart_asset_trend", col_span: 1, sort_order: 110, style_config: { variant: "default", density: "compact", chart_type: "line" }, data_source_config: {}, is_active: true },
  { widget_key: "chart_license_expiry", title: "软件授权到期分布", widget_type: "chart", metric_key: "chart_license_expiry", col_span: 1, sort_order: 120, style_config: { variant: "default", density: "compact", chart_type: "bar" }, data_source_config: {}, is_active: true },
  { widget_key: "chart_system_dev_lang", title: "系统开发语言", widget_type: "chart", metric_key: "chart_system_dev_lang", col_span: 1, sort_order: 130, style_config: { variant: "default", density: "compact", chart_type: "bar" }, data_source_config: { top_n: 8 }, is_active: true },
  { widget_key: "chart_system_status", title: "系统资产状态", widget_type: "chart", metric_key: "chart_system_status", col_span: 1, sort_order: 140, style_config: { variant: "default", density: "compact", chart_type: "donut" }, data_source_config: { top_n: 8 }, is_active: true },
];

const templateId = ref(null);
const widgets = ref([...defaultWidgets]);
const designerOpen = ref(false);
const editingWidgets = ref([]);
const saving = ref(false);

const hasPermission = (resource, action = "view") => {
  const roleCode = localStorage.getItem("roleCode") || "";
  if (roleCode === "super_admin") return true;
  const raw = localStorage.getItem("assethub_permissions");
  if (!raw) return false;
  try {
    const perms = JSON.parse(raw);
    return perms.includes(`${resource}:${action}`);
  } catch {
    return false;
  }
};

const canEditDashboard = computed(() => hasPermission("dashboard", "edit"));
const canPublishDashboard = computed(() => hasPermission("dashboard", "publish"));

const sortedActiveWidgets = computed(() =>
  [...widgets.value]
    .filter((item) => item && item.is_active !== false)
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
);
const kpiWidgets = computed(() => sortedActiveWidgets.value.filter((item) => item.widget_type === "kpi"));
const chartWidgets = computed(() => sortedActiveWidgets.value.filter((item) => item.widget_type === "chart"));

const cardVariantClass = (variant) => {
  if (variant === "soft") return "border";
  if (variant === "outline") return "border";
  return "border bg-background";
};
const widgetCardStyle = (widget, gridStyle = {}) => {
  const variant = String(widget?.style_config?.variant || "default");
  const style = { ...(gridStyle || {}) };
  if (variant === "soft") {
    style.backgroundColor = "hsl(var(--accent) / 0.35)";
  } else if (variant === "outline") {
    style.backgroundColor = "hsl(var(--background))";
  } else {
    style.backgroundColor = "hsl(var(--background))";
  }
  return style;
};

const densityClass = (density) => (density === "normal" ? "chart-card-normal" : "chart-card-compact");
const chartHeight = (widget) => (widget?.style_config?.density === "normal" ? 240 : 180);
const kpiGridStyle = (widget) => ({ gridColumn: `span ${Math.max(1, Math.min(5, Number(widget?.col_span || 1)))}` });
const chartGridStyle = (widget) => ({ gridColumn: `span ${Math.max(1, Math.min(3, Number(widget?.col_span || 1)))}` });
const defaultChartType = (metricKey) => (metricKey === "chart_asset_trend" ? "line" : metricKey === "chart_system_status" || metricKey === "chart_asset_status" ? "donut" : "bar");
const chartType = (widget) => String(widget?.style_config?.chart_type || defaultChartType(widget?.metric_key));
const isDonutType = (widget) => {
  const type = chartType(widget);
  return type === "donut" || type === "pie";
};

const refresh = async () => {
  try {
    const res = await api.get("/dashboard");
    if (res?.data && typeof res.data === "object") {
      data.value = { ...data.value, ...res.data };
      const template = res.data.template;
      if (template?.id) {
        templateId.value = template.id;
        widgets.value = (template.widgets || []).map(normalizeWidget);
      }
    }
  } catch (error) {
    console.error("Dashboard load failed", error);
    toast.error("加载看板数据失败");
  }
};

const normalizeWidget = (item) => ({
  id: item.id || null,
  widget_key: item.widget_key,
  title: item.title || item.widget_key,
  widget_type: item.widget_type || "chart",
  metric_key: item.metric_key,
  col_span: Math.max(1, Math.min(3, Number(item.col_span || 1))),
  row_span: Math.max(1, Number(item.row_span || 1)),
  sort_order: Number(item.sort_order || 0),
  style_config: { variant: "default", density: "compact", chart_type: defaultChartType(item.metric_key), ...(item.style_config || {}) },
  data_source_config: { ...(item.data_source_config || {}) },
  is_active: item.is_active !== false,
});

const formatKpiValue = (metricKey) => {
  if (metricKey === "kpi_total_assets") return data.value.total ?? 0;
  if (metricKey === "kpi_in_use_rate") return `${((data.value.in_use_rate || 0) * 100).toFixed(1)}%`;
  if (metricKey === "kpi_repairing") return data.value.repairing ?? 0;
  if (metricKey === "kpi_pending_scrap") return data.value.pending_scrap ?? 0;
  if (metricKey === "kpi_license_warn") return data.value.license_expire_warn ?? 0;
  return "-";
};

const chartColor = (key) => `var(--color-${key})`;
const seriesPalette = ["var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)", "var(--chart-1)"];
const buildSeriesConfig = (series = []) =>
  series.reduce((acc, item, index) => {
    acc[item.key] = { label: item.label, color: seriesPalette[index % seriesPalette.length] };
    return acc;
  }, {});

const topNFromWidget = (widget, fallback = 0) => {
  const raw = Number(widget?.data_source_config?.top_n || 0);
  if (!Number.isFinite(raw) || raw <= 0) return fallback;
  return Math.min(50, Math.max(1, raw));
};

const assetStatusSeries = (widget) => {
  const counts = data.value.status_counts || {};
  const source = [
    { key: "idle", label: "库存", value: counts.idle || 0 },
    { key: "in_use", label: "在用", value: counts.in_use || 0 },
    { key: "repairing", label: "维修", value: counts.repairing || 0 },
    { key: "pending_scrap", label: "待报废", value: counts.pending_scrap || 0 },
    { key: "scrapped", label: "已报废", value: counts.scrapped || 0 },
  ].filter((item) => item.value > 0);
  const topN = topNFromWidget(widget, 0);
  return topN > 0 ? source.slice(0, topN) : source;
};
const assetStatusBarData = (widget) => assetStatusSeries(widget).map((item, index) => ({ ...item, index }));
const assetStatusLabel = (widget) => (_, index) => assetStatusBarData(widget)[index]?.label || "";

const monthlyData = computed(() => {
  const raw = Array.isArray(data.value.monthly_assets) ? data.value.monthly_assets : [];
  const source = raw.length ? raw : buildMonthlyFallback();
  return source.map((item, index) => ({ index, month: item.month, count: Number(item.count || 0) }));
});

const licenseData = computed(() => {
  const buckets = data.value.license_expire_buckets || {};
  return [
    { index: 0, label: "30天内", value: Number(buckets.d30 || 0) },
    { index: 1, label: "31-60天", value: Number(buckets.d60 || 0) },
    { index: 2, label: "61-90天", value: Number(buckets.d90 || 0) },
  ];
});

const systemStatusData = (widget) => {
  const source = (data.value.system_status_counts || []).map((item, index) => ({
    index,
    key: `system_status_${index}`,
    label: item.label || "未设置",
    value: Number(item.value || 0),
  }));
  const sorted = source.sort((a, b) => b.value - a.value);
  const topN = topNFromWidget(widget, 0);
  return topN > 0 ? sorted.slice(0, topN) : sorted;
};

const devLangData = (widget) => {
  const source = (data.value.system_dev_lang_counts || []).map((item, index) => ({
    index,
    key: `dev_lang_${index}`,
    label: item.label || "未设置",
    value: Number(item.value || 0),
  }));
  const sorted = source.sort((a, b) => b.value - a.value);
  const topN = topNFromWidget(widget, 8);
  return topN > 0 ? sorted.slice(0, topN) : sorted;
};

const systemStatusTotal = (widget) => systemStatusData(widget).reduce((sum, item) => sum + item.value, 0);
const devLangTotal = (widget) => devLangData(widget).reduce((sum, item) => sum + item.value, 0);
const systemStatusConfig = (widget) => buildSeriesConfig(systemStatusData(widget));
const devLangChartConfig = (widget) => buildSeriesConfig(devLangData(widget));
const systemStatusLabel = (widget) => (_, index) => systemStatusData(widget)[index]?.label || "";

const statusChartConfig = {
  idle: { label: "库存", color: "var(--chart-2)" },
  in_use: { label: "在用", color: "var(--chart-3)" },
  repairing: { label: "维修", color: "var(--chart-4)" },
  pending_scrap: { label: "待报废", color: "var(--chart-5)" },
  scrapped: { label: "已报废", color: "var(--chart-1)" },
};
const trendChartConfig = { assets: { label: "新增资产", color: "var(--chart-3)" } };
const licenseChartConfig = { license: { label: "到期授权", color: "var(--chart-4)" } };

const formatMonth = (_, index) => monthlyData.value[index]?.month || "";
const formatLicenseLabel = (_, index) => licenseData.value[index]?.label || "";
const formatDevLangLabel = (widget) => (_, index) => devLangData(widget)[index]?.label || "";

const trendTooltip = (datum) => {
  if (!datum) return "";
  return componentToString(ChartTooltipContent, {
    title: datum.month || "",
    items: [{ label: "新增资产", value: datum.count ?? 0, color: chartColor("assets") }],
  });
};
const trendBarTooltip = (datum) => trendTooltip(datum);

const licenseTooltip = (datum) => {
  if (!datum) return "";
  return componentToString(ChartTooltipContent, {
    title: datum.label || "",
    items: [{ label: "到期授权", value: datum.value ?? 0, color: chartColor("license") }],
  });
};

const donutTooltip = (datum) => {
  if (!datum) return "";
  const raw = datum.data ?? datum;
  const label = raw.label || "资产状态";
  const value = raw.value ?? datum.value ?? 0;
  return componentToString(ChartTooltipContent, {
    title: label,
    items: [{ label, value, color: raw.key ? chartColor(raw.key) : "var(--muted-foreground)" }],
  });
};

const systemStatusTooltip = (datum) => {
  if (!datum) return "";
  const raw = datum.data ?? datum;
  const label = raw.label || "系统状态";
  const value = raw.value ?? datum.value ?? 0;
  return componentToString(ChartTooltipContent, {
    title: label,
    items: [{ label, value, color: raw.key ? chartColor(raw.key) : "var(--muted-foreground)" }],
  });
};

const devLangTooltip = (datum) => {
  if (!datum) return "";
  const raw = datum.data ?? datum;
  const label = raw.label || "开发语言";
  const value = raw.value ?? datum.value ?? 0;
  return componentToString(ChartTooltipContent, {
    title: label,
    items: [{ label, value, color: raw.key ? chartColor(raw.key) : "var(--muted-foreground)" }],
  });
};
const devLangDonutTooltip = (datum) => devLangTooltip(datum);
const systemStatusBarTooltip = (datum) => systemStatusTooltip(datum);

const buildMonthlyFallback = () => {
  const now = new Date();
  const list = [];
  for (let i = 11; i >= 0; i -= 1) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    list.push({ month, count: 0 });
  }
  return list;
};

const openDesigner = () => {
  editingWidgets.value = [...widgets.value].map((item) => ({
    ...item,
    style_config: { variant: "default", density: "compact", chart_type: defaultChartType(item.metric_key), ...(item.style_config || {}) },
    data_source_config: { ...(item.data_source_config || {}) },
  }));
  designerOpen.value = true;
};

const metricOptionsFor = (widgetType) => {
  if (widgetType === "kpi") {
    return [
      { value: "kpi_total_assets", label: "总资产" },
      { value: "kpi_in_use_rate", label: "在用率" },
      { value: "kpi_repairing", label: "维修中" },
      { value: "kpi_pending_scrap", label: "待报废" },
      { value: "kpi_license_warn", label: "授权到期预警" },
    ];
  }
  return [
    { value: "chart_asset_status", label: "资产状态分布" },
    { value: "chart_asset_trend", label: "近12个月新增趋势" },
    { value: "chart_license_expiry", label: "软件授权到期分布" },
    { value: "chart_system_dev_lang", label: "系统开发语言" },
    { value: "chart_system_status", label: "系统资产状态" },
  ];
};
const chartTypeOptionsForMetric = (metricKey) => {
  if (metricKey === "chart_asset_trend") {
    return [
      { value: "line", label: "折线图" },
      { value: "bar", label: "柱状图" },
    ];
  }
  return [
    { value: "bar", label: "柱状图" },
    { value: "donut", label: "环形图" },
    { value: "pie", label: "饼图" },
  ];
};

const saveDashboardDraft = async () => {
  if (!templateId.value) {
    toast.error("当前看板模板不存在");
    return;
  }
  saving.value = true;
  try {
    const payload = {
      widgets: editingWidgets.value.map((item, index) => ({
        id: item.id || null,
        widget_key: item.widget_key,
        title: String(item.title || item.widget_key),
        widget_type: item.widget_type,
        metric_key: item.metric_key,
        col_span: Number(item.col_span || 1),
        row_span: Number(item.row_span || 1),
        sort_order: Number(item.sort_order ?? index * 10),
        style_config: item.style_config || {},
        data_source_config: item.data_source_config || {},
        is_active: item.is_active !== false,
      })),
    };
    const res = await api.put(`/dashboard/templates/${templateId.value}/widgets`, payload);
    widgets.value = (res?.data?.widgets || []).map(normalizeWidget);
    designerOpen.value = false;
    toast.success("看板草稿已保存");
  } catch (error) {
    console.error("save dashboard draft failed", error);
    toast.error(error?.response?.data?.detail || "保存草稿失败");
  } finally {
    saving.value = false;
  }
};

const buildWidgetsPayload = () => ({
  widgets: editingWidgets.value.map((item, index) => ({
    id: item.id || null,
    widget_key: item.widget_key,
    title: String(item.title || item.widget_key),
    widget_type: item.widget_type,
    metric_key: item.metric_key,
    col_span: Number(item.col_span || 1),
    row_span: Number(item.row_span || 1),
    sort_order: Number(item.sort_order ?? index * 10),
    style_config: item.style_config || {},
    data_source_config: item.data_source_config || {},
    is_active: item.is_active !== false,
  })),
});

const publishDashboard = async () => {
  if (!templateId.value) {
    toast.error("当前看板模板不存在");
    return;
  }
  saving.value = true;
  try {
    const draftRes = await api.put(`/dashboard/templates/${templateId.value}/widgets`, buildWidgetsPayload());
    widgets.value = (draftRes?.data?.widgets || []).map(normalizeWidget);
    await api.post(`/dashboard/templates/${templateId.value}/publish`);
    designerOpen.value = false;
    toast.success("看板已发布");
    await refresh();
  } catch (error) {
    console.error("publish dashboard failed", error);
    toast.error(error?.response?.data?.detail || "发布失败");
  } finally {
    saving.value = false;
  }
};

onMounted(async () => {
  await refresh();
  if (!templateId.value) {
    widgets.value = [...defaultWidgets];
  }
});
</script>

<style scoped>
.dashboard-page {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.hero-panel {
  position: relative;
  overflow: hidden;
  border: 1px solid hsl(var(--border));
  border-radius: 1.1rem;
  background:
    radial-gradient(circle at 6% 0%, hsl(var(--chart-2) / 0.25), transparent 42%),
    radial-gradient(circle at 100% 0%, hsl(var(--chart-1) / 0.22), transparent 40%),
    linear-gradient(135deg, hsl(var(--background)), hsl(var(--muted) / 0.4)),
    hsl(var(--background));
  box-shadow: 0 12px 28px hsl(var(--foreground) / 0.08), inset 0 1px 0 hsl(var(--background));
}

.hero-panel::after {
  content: "";
  position: absolute;
  top: -52px;
  right: -40px;
  width: 220px;
  height: 220px;
  border-radius: 9999px;
  background: radial-gradient(circle, hsl(var(--chart-2) / 0.18), transparent 72%);
  pointer-events: none;
}

.hero-eyebrow {
  margin-bottom: 0.25rem;
  color: hsl(var(--muted-foreground));
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero-title {
  margin: 0;
  font-size: 1.6rem;
  line-height: 1.2;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.hero-desc {
  margin-top: 0.35rem;
  color: hsl(var(--muted-foreground));
  font-size: 0.9rem;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  height: 2.1rem;
  padding: 0 0.8rem;
  border: 1px solid hsl(var(--border));
  border-radius: 9999px;
  background: linear-gradient(180deg, hsl(var(--background)), hsl(var(--muted) / 0.35));
  color: hsl(var(--foreground));
  font-weight: 600;
  font-size: 0.8rem;
  box-shadow: 0 4px 14px hsl(var(--foreground) / 0.08);
}

.kpi-grid,
.chart-grid {
  position: relative;
}

.card {
  position: relative;
  overflow: hidden;
  border-radius: 0.9rem;
  padding: 1rem 1rem 0.95rem;
  background: linear-gradient(180deg, hsl(var(--background)), hsl(var(--muted) / 0.22));
  transition: transform 0.16s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  box-shadow: 0 6px 16px hsl(var(--foreground) / 0.06), 0 20px 32px hsl(var(--foreground) / 0.07);
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 22px hsl(var(--foreground) / 0.08), 0 24px 44px hsl(var(--foreground) / 0.1);
}

.label {
  color: hsl(var(--muted-foreground));
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.value {
  margin-top: 0.45rem;
  font-size: 1.75rem;
  line-height: 1.1;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.kpi-card {
  background:
    linear-gradient(180deg, hsl(var(--background)), hsl(var(--muted) / 0.35)),
    linear-gradient(90deg, hsl(var(--chart-1) / 0.14), transparent 46%);
}

.kpi-card::before {
  content: "";
  position: absolute;
  left: 0.9rem;
  right: 0.9rem;
  top: 0.7rem;
  height: 2px;
  border-radius: 9999px;
  background: linear-gradient(90deg, hsl(var(--chart-2)), hsl(var(--chart-1) / 0.1));
  opacity: 0.85;
}

.chart-card {
  display: flex;
  flex-direction: column;
  padding-top: 0.92rem;
  background:
    linear-gradient(180deg, hsl(var(--background)), hsl(var(--muted) / 0.2)),
    radial-gradient(circle at 100% 0%, hsl(var(--chart-1) / 0.08), transparent 35%);
}

.chart-card-compact {
  min-height: 258px;
}

.chart-card-normal {
  min-height: 330px;
}

.chart-title {
  margin-bottom: 0.8rem;
  font-size: 0.93rem;
  letter-spacing: 0.01em;
  font-weight: 700;
  color: hsl(var(--foreground));
  padding-left: 0.55rem;
  border-left: 3px solid hsl(var(--chart-2) / 0.75);
}

.chart-body {
  flex: 1;
}

.chart-shell :deep([data-vis-container]) {
  width: 100%;
}

.chart-split {
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-wrap {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: center;
}

@media (max-width: 900px) {
  .hero-title {
    font-size: 1.28rem;
  }

  .card:hover {
    transform: none;
  }
}
</style>
