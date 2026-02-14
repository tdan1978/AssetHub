<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="grid gap-4 md:grid-cols-4 items-end">
        <div class="form-field">
          <label class="form-label">关键词</label>
          <Input v-model="q" placeholder="搜索系统名称/编码" />
        </div>
        <div class="form-field">
          <label class="form-label">系统状态</label>
          <Select v-model="status">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="系统状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              <SelectItem value="开发中">开发中</SelectItem>
              <SelectItem value="测试中">测试中</SelectItem>
              <SelectItem value="运行中">运行中</SelectItem>
              <SelectItem value="维护中">维护中</SelectItem>
              <SelectItem value="已下线">已下线</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="md:col-span-2 flex items-end gap-3">
          <Button :disabled="loading" @click="loadAggregatedTopology">刷新聚合拓扑</Button>
          <div class="text-xs text-muted-foreground">
            系统 {{ stats.systems }} / 节点 {{ stats.nodes }} / 连线 {{ stats.edges }}
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-lg border bg-background p-4">
      <div v-if="loading" class="flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground">
        <Spinner class="size-5" />
        <span>正在生成聚合拓扑...</span>
      </div>
      <div v-else-if="!stats.nodes" class="py-10 text-center text-sm text-muted-foreground">
        未找到可展示的系统拓扑数据
      </div>
      <TopologyCanvas v-else :model-value="mergedTopology" :readonly="true" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Spinner } from "../components/ui/spinner";
import TopologyCanvas from "../components/topology/TopologyCanvas.vue";

const q = ref("");
const status = ref("all");
const loading = ref(false);
const mergedTopology = ref("");
const stats = reactive({
  systems: 0,
  nodes: 0,
  edges: 0,
});

const parseTopologyObject = (raw) => {
  try {
    const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
    return {
      nodes: Array.isArray(parsed?.nodes) ? parsed.nodes : [],
      edges: Array.isArray(parsed?.edges) ? parsed.edges : [],
      viewport: parsed?.viewport && typeof parsed.viewport === "object" ? parsed.viewport : { x: 0, y: 0, zoom: 1 },
      options: parsed?.options && typeof parsed.options === "object" ? parsed.options : { constrainToGroup: true },
    };
  } catch {
    return {
      nodes: [],
      edges: [],
      viewport: { x: 0, y: 0, zoom: 1 },
      options: { constrainToGroup: true },
    };
  }
};

const getNodeSize = (node) => {
  if (!node) return { width: 120, height: 48 };
  if (node.type === "group") {
    const width = Number.parseFloat(String(node?.style?.width ?? node?.width ?? 280));
    const height = Number.parseFloat(String(node?.style?.height ?? node?.height ?? 180));
    return {
      width: Number.isFinite(width) ? Math.max(120, width) : 280,
      height: Number.isFinite(height) ? Math.max(80, height) : 180,
    };
  }
  const width = Number.parseFloat(String(node?.data?.width ?? 120));
  const height = Number.parseFloat(String(node?.data?.height ?? 48));
  return {
    width: Number.isFinite(width) ? Math.max(80, width) : 120,
    height: Number.isFinite(height) ? Math.max(40, height) : 48,
  };
};

const getTopologyBounds = (nodes) => {
  if (!Array.isArray(nodes) || !nodes.length) return { minX: 0, minY: 0, width: 0, height: 0 };
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;
  for (const node of nodes) {
    const x = Number(node?.position?.x || 0);
    const y = Number(node?.position?.y || 0);
    const size = getNodeSize(node);
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x + size.width);
    maxY = Math.max(maxY, y + size.height);
  }
  return { minX, minY, width: Math.max(0, maxX - minX), height: Math.max(0, maxY - minY) };
};

const fetchSystems = async () => {
  const size = 100;
  let page = 1;
  let all = [];
  while (true) {
    const { data } = await api.get("/systems", {
      params: {
        page,
        size,
        q: q.value || null,
        app_status: status.value === "all" ? null : status.value,
      },
    });
    const chunk = Array.isArray(data?.items) ? data.items : [];
    all = [...all, ...chunk];
    if (chunk.length < size) break;
    page += 1;
  }
  return all;
};

const loadAggregatedTopology = async () => {
  loading.value = true;
  try {
    const [systems, categoriesRes] = await Promise.all([
      fetchSystems(),
      api.get("/system-field-categories/tree"),
    ]);

    const topologyFieldIds = new Set();
    for (const category of categoriesRes.data || []) {
      for (const field of category?.fields || []) {
        if (field?.field_type === "topology") topologyFieldIds.add(Number(field.id));
      }
    }

    const fieldResponses = await Promise.all(
      systems.map(async (system) => {
        try {
          const { data } = await api.get(`/systems/${system.id}/fields`);
          return { system, fields: Array.isArray(data) ? data : [] };
        } catch {
          return { system, fields: [] };
        }
      })
    );

    const aggregatedNodes = [];
    const aggregatedEdges = [];
    const anchorBySystemId = new Map();
    const dedupEdgeKeys = new Set();

    const layoutItems = fieldResponses.map(({ system, fields }) => {
      const topologyField = fields.find((item) => topologyFieldIds.has(Number(item?.field_id)));
      const topology = parseTopologyObject(topologyField?.value || "");
      const systemId = Number(system.id);
      const prefix = `sys-${systemId}::`;
      const mapId = (id) => `${prefix}${id}`;
      const topLevelNodes = topology.nodes.filter((node) => !node?.parentNode);
      const bounds = getTopologyBounds(topLevelNodes.length ? topLevelNodes : topology.nodes);
      const redirectNodeToAnchor = new Map();
      const removedSystemNodeIds = new Set();
      for (const node of topology.nodes) {
        const targetSystemId = Number(node?.data?.systemId || 0);
        if (!Number.isFinite(targetSystemId) || targetSystemId <= 0 || targetSystemId === systemId) continue;
        removedSystemNodeIds.add(String(node.id));
      }

      const contentWidth = Math.max(220, bounds.width);
      const contentHeight = Math.max(120, bounds.height);
      const paddingX = 48;
      const headerHeight = 76;
      const footerPadding = 36;
      const groupWidth = Math.min(1200, Math.max(560, contentWidth + paddingX * 2));
      const groupHeight = Math.min(920, Math.max(320, contentHeight + headerHeight + footerPadding));

      return {
        system,
        systemId,
        topology,
        mapId,
        removedSystemNodeIds,
        redirectNodeToAnchor,
        bounds,
        paddingX,
        headerHeight,
        groupWidth,
        groupHeight,
      };
    });

    const systemCount = layoutItems.length;
    const cols = systemCount <= 2 ? Math.max(1, systemCount) : systemCount <= 4 ? 2 : systemCount <= 9 ? 3 : 4;
    const gapX = 120;
    const gapY = 100;
    const marginX = 80;
    const marginY = 80;

    const colWidths = Array.from({ length: cols }, () => 0);
    const rowHeights = Array.from({ length: Math.ceil(systemCount / cols) }, () => 0);
    layoutItems.forEach((item, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      colWidths[col] = Math.max(colWidths[col], item.groupWidth);
      rowHeights[row] = Math.max(rowHeights[row], item.groupHeight);
    });

    const colOffsets = [];
    let colCursor = 0;
    for (let i = 0; i < colWidths.length; i += 1) {
      colOffsets.push(colCursor);
      colCursor += colWidths[i] + gapX;
    }

    const rowOffsets = [];
    let rowCursor = 0;
    for (let i = 0; i < rowHeights.length; i += 1) {
      rowOffsets.push(rowCursor);
      rowCursor += rowHeights[i] + gapY;
    }

    layoutItems.forEach((item, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      const groupX = marginX + colOffsets[col];
      const groupY = marginY + rowOffsets[row];
      const groupId = `sys-group-${item.systemId}`;
      const anchorId = `sys-anchor-${item.systemId}`;

      aggregatedNodes.push({
        id: groupId,
        type: "group",
        position: { x: groupX, y: groupY },
        style: {
          width: `${item.groupWidth}px`,
          height: `${item.groupHeight}px`,
        },
        data: {
          label: item.system.app_name || item.system.app_code || `系统 ${item.systemId}`,
          hideHandles: true,
          bgColor: "#f8fafc",
          borderColor: "#94a3b8",
          borderRadius: 12,
        },
      });

      aggregatedNodes.push({
        id: anchorId,
        type: "editable",
        parentNode: groupId,
        extent: "parent",
        position: { x: 24, y: 24 },
        data: {
          label: item.system.app_name || item.system.app_code || `系统 ${item.systemId}`,
          systemId: String(item.systemId),
          nodeKind: "system-anchor",
          icon: "boxes",
          bgColor: "#dbeafe",
          borderColor: "#3b82f6",
          textColor: "#1e3a8a",
          width: 220,
          height: 52,
          borderRadius: 10,
          fontSize: 14,
          textAlign: "center",
          verticalAlign: "center",
          hideHandles: true,
        },
      });
      anchorBySystemId.set(item.systemId, anchorId);
    });

    layoutItems.forEach((item) => {
      const groupId = `sys-group-${item.systemId}`;

      for (const node of item.topology.nodes) {
        if (item.removedSystemNodeIds.has(String(node.id))) continue;

        const rawParentId = node?.parentNode ? String(node.parentNode) : "";
        const parentRemoved = rawParentId ? item.removedSystemNodeIds.has(rawParentId) : false;
        const mappedParent = rawParentId && !parentRemoved ? item.mapId(rawParentId) : groupId;

        const nextNode = {
          ...node,
          id: item.mapId(node.id),
          parentNode: mappedParent,
          extent: "parent",
        };

        if (!rawParentId || parentRemoved) {
          nextNode.position = {
            x: Number(node?.position?.x || 0) - item.bounds.minX + item.paddingX,
            y: Number(node?.position?.y || 0) - item.bounds.minY + item.headerHeight,
          };
        }

        aggregatedNodes.push(nextNode);
      }

      for (const node of item.topology.nodes) {
        const targetSystemId = Number(node?.data?.systemId || 0);
        if (!Number.isFinite(targetSystemId) || targetSystemId <= 0 || targetSystemId === item.systemId) continue;
        const targetAnchorId = anchorBySystemId.get(targetSystemId);
        if (!targetAnchorId) continue;
        item.redirectNodeToAnchor.set(String(node.id), targetAnchorId);
      }

      for (const edge of item.topology.edges) {
        const sourceId = String(edge?.source || "");
        const targetId = String(edge?.target || "");
        const redirectedSource = item.redirectNodeToAnchor.get(sourceId) || item.mapId(sourceId);
        const redirectedTarget = item.redirectNodeToAnchor.get(targetId) || item.mapId(targetId);
        if (!redirectedSource || !redirectedTarget || redirectedSource === redirectedTarget) continue;
        const edgeKey = `${redirectedSource}=>${redirectedTarget}`;
        if (dedupEdgeKeys.has(edgeKey)) continue;
        dedupEdgeKeys.add(edgeKey);

        const isCrossSystem = String(redirectedSource).startsWith("sys-anchor-") || String(redirectedTarget).startsWith("sys-anchor-");
        aggregatedEdges.push({
          ...edge,
          id: item.mapId(edge.id),
          source: redirectedSource,
          target: redirectedTarget,
          animated: isCrossSystem || !!edge?.animated,
          markerEnd: isCrossSystem ? "arrowclosed" : edge?.markerEnd,
          style: isCrossSystem
            ? { ...(edge?.style || {}), stroke: "#2563eb", strokeWidth: 2, strokeDasharray: "6 4" }
            : edge?.style,
        });
      }
    });

    const merged = {
      nodes: aggregatedNodes,
      edges: aggregatedEdges,
      viewport: { x: 0, y: 0, zoom: 0.55 },
      options: { constrainToGroup: true },
    };
    mergedTopology.value = JSON.stringify(merged);
    stats.systems = systems.length;
    stats.nodes = aggregatedNodes.length;
    stats.edges = aggregatedEdges.length;
  } finally {
    loading.value = false;
  }
};

onMounted(loadAggregatedTopology);
</script>



