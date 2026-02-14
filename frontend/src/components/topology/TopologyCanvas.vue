<template>
  <div class="space-y-2">
    <div v-if="!readonly" class="flex flex-wrap items-center gap-2">
      <Button size="sm" variant="outline" type="button" @click="addNode">添加节点</Button>
      <Button size="sm" variant="outline" type="button" @click="addTextNode">添加文本框</Button>
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button size="sm" variant="outline" type="button">添加系统节点</Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent class="w-64 p-2" align="start">
          <Input
            v-model="systemNodeKeyword"
            class="mb-2 h-8 text-xs"
            placeholder="搜索系统"
            @keydown.stop
            @pointerdown.stop
          />
          <div class="max-h-64 overflow-y-auto overscroll-contain" @wheel.stop>
            <DropdownMenuItem
              v-for="item in filteredSystemNodeItems"
              :key="item.value"
              @click="addSystemNode(item.value)"
            >
              {{ item.label }}
            </DropdownMenuItem>
            <DropdownMenuItem v-if="!filteredSystemNodeItems.length" disabled>暂无可选系统</DropdownMenuItem>
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
      <Button size="sm" variant="outline" type="button" @click="addGroup">添加分组</Button>
      <Button size="sm" variant="outline" type="button" :disabled="!selectedNode && !selectedEdge" @click="removeSelected">
        删除选中
      </Button>
      <span class="ml-1 text-xs text-muted-foreground">新节点分组</span>
      <div class="w-40">
        <Combobox v-model="newNodeGroupId" :options="groupOptionsWithNone" placeholder="选择分组" />
      </div>
      <div class="ml-1 flex items-center gap-1.5 text-xs">
        <Switch v-model:checked="constrainToGroup" />
        <span class="text-muted-foreground">限制子节点在分组内</span>
      </div>
      <div class="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
        <span>节点 {{ nodes.length }}</span>
        <span>连线 {{ edges.length }}</span>
      </div>
    </div>

    <div v-if="!readonly" class="h-[104px]">
      <div
        v-if="selectedNode && selectedNode.type !== 'group' && !selectedNodeIsText"
        class="flex h-full flex-wrap items-center gap-1.5 overflow-y-auto rounded-md border bg-muted/20 p-2 text-xs"
      >
        <span class="rounded bg-primary/10 px-1.5 py-0.5 font-medium text-primary">节点属性</span>
        <span class="text-muted-foreground">名称</span>
        <Input
          v-model="selectedNodeLabel"
          class="h-7 w-40 text-xs"
          placeholder="节点名称"
          :readonly="selectedNodeIsSystem"
        />
        <span class="text-muted-foreground">图标</span>
        <div class="w-36">
          <Combobox v-model="selectedNodeIcon" :options="TOPOLOGY_ICON_OPTIONS" placeholder="选择图标" />
        </div>
        <span class="text-muted-foreground">宽</span>
        <Input v-model="selectedNodeWidth" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">高</span>
        <Input v-model="selectedNodeHeight" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">圆角</span>
        <Input v-model="selectedNodeRadius" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">字号</span>
        <Input v-model="selectedNodeFontSize" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">横向</span>
        <select v-model="selectedNodeTextAlign" class="h-7 rounded-md border bg-background px-2 text-xs">
          <option value="left">左</option>
          <option value="center">中</option>
          <option value="right">右</option>
        </select>
        <span class="text-muted-foreground">纵向</span>
        <select v-model="selectedNodeVerticalAlign" class="h-7 rounded-md border bg-background px-2 text-xs">
          <option value="top">上</option>
          <option value="center">中</option>
          <option value="bottom">下</option>
        </select>
        <span class="text-muted-foreground">背景</span>
        <input v-model="selectedNodeBgColor" type="color" class="h-7 w-9 rounded border p-0.5" />
        <span class="text-muted-foreground">边框</span>
        <input v-model="selectedNodeBorderColor" type="color" class="h-7 w-9 rounded border p-0.5" />
        <span class="text-muted-foreground">文字</span>
        <input v-model="selectedNodeTextColor" type="color" class="h-7 w-9 rounded border p-0.5" />
        <span class="text-muted-foreground">所属分组</span>
        <div class="w-40">
          <Combobox v-model="selectedNodeGroupId" :options="groupOptionsWithNone" placeholder="选择分组" />
        </div>
        <Button
          size="sm"
          variant="outline"
          type="button"
          class="h-7 px-2 text-xs"
          :disabled="!selectedNode || selectedNode.type === 'group' || !selectedNodeGroupId || selectedNodeGroupId === '__none__'"
          @click="moveSelectedNodeToGroup"
        >
          加入分组
        </Button>
        <Button
          size="sm"
          variant="outline"
          type="button"
          class="h-7 px-2 text-xs"
          :disabled="!selectedNode || selectedNode.type === 'group' || !selectedNode.parentNode"
          @click="removeSelectedNodeFromGroup"
        >
          移出分组
        </Button>
      </div>

      <div
        v-else-if="selectedNode && selectedNode.type !== 'group' && selectedNodeIsText"
        class="flex h-full flex-wrap items-center gap-1.5 overflow-y-auto rounded-md border bg-muted/20 p-2 text-xs"
      >
        <span class="rounded bg-primary/10 px-1.5 py-0.5 font-medium text-primary">文本属性</span>
        <span class="text-muted-foreground">文字</span>
        <Input v-model="selectedNodeLabel" class="h-7 w-64 text-xs" placeholder="输入文本（可留空）" />
        <span class="text-muted-foreground">字号</span>
        <Input v-model="selectedNodeFontSize" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">对齐</span>
        <select v-model="selectedNodeTextAlign" class="h-7 rounded-md border bg-background px-2 text-xs">
          <option value="left">左</option>
          <option value="center">中</option>
          <option value="right">右</option>
        </select>
        <span class="text-muted-foreground">文字</span>
        <input v-model="selectedNodeTextColor" type="color" class="h-7 w-9 rounded border p-0.5" />
        <span class="text-muted-foreground">所属分组</span>
        <div class="w-40">
          <Combobox v-model="selectedNodeGroupId" :options="groupOptionsWithNone" placeholder="选择分组" />
        </div>
        <Button
          size="sm"
          variant="outline"
          type="button"
          class="h-7 px-2 text-xs"
          :disabled="!selectedNode || selectedNode.type === 'group' || !selectedNodeGroupId || selectedNodeGroupId === '__none__'"
          @click="moveSelectedNodeToGroup"
        >
          加入分组
        </Button>
        <Button
          size="sm"
          variant="outline"
          type="button"
          class="h-7 px-2 text-xs"
          :disabled="!selectedNode || selectedNode.type === 'group' || !selectedNode.parentNode"
          @click="removeSelectedNodeFromGroup"
        >
          移出分组
        </Button>
      </div>

      <div
        v-else-if="selectedNode && selectedNode.type === 'group'"
        class="flex h-full flex-wrap items-center gap-1.5 overflow-y-auto rounded-md border bg-muted/20 p-2 text-xs"
      >
        <span class="rounded bg-primary/10 px-1.5 py-0.5 font-medium text-primary">分组属性</span>
        <span class="text-muted-foreground">名称</span>
        <Input v-model="selectedNodeLabel" class="h-7 w-40 text-xs" placeholder="分组名称" />
        <span class="text-muted-foreground">宽</span>
        <Input v-model="selectedGroupWidth" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">高</span>
        <Input v-model="selectedGroupHeight" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">圆角</span>
        <Input v-model="selectedGroupRadius" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">背景</span>
        <input v-model="selectedGroupBgColor" type="color" class="h-7 w-9 rounded border p-0.5" />
        <span class="text-muted-foreground">边框</span>
        <input v-model="selectedGroupBorderColor" type="color" class="h-7 w-9 rounded border p-0.5" />
      </div>

      <div v-else-if="selectedEdge" class="flex h-full flex-wrap items-center gap-1.5 overflow-y-auto rounded-md border bg-muted/20 p-2 text-xs">
        <span class="rounded bg-primary/10 px-1.5 py-0.5 font-medium text-primary">连线属性</span>
        <span class="text-muted-foreground">颜色</span>
        <input v-model="selectedEdgeColor" type="color" class="h-7 w-9 rounded border p-0.5" />
        <span class="text-muted-foreground">粗细</span>
        <Input v-model="selectedEdgeWidth" class="h-7 w-16 text-xs" type="number" />
        <span class="text-muted-foreground">线型</span>
        <select v-model="selectedEdgeLineType" class="h-7 rounded-md border bg-background px-2 text-xs">
          <option value="solid">实线</option>
          <option value="dashed">虚线</option>
          <option value="dotted">点线</option>
          <option value="dashdot">点划线</option>
        </select>
        <span class="text-muted-foreground">路径</span>
        <select v-model="selectedEdgePathType" class="h-7 rounded-md border bg-background px-2 text-xs">
          <option value="default">曲线</option>
          <option value="smoothstep">平滑折线</option>
          <option value="step">阶梯线</option>
          <option value="straight">直线</option>
        </select>
        <span class="text-muted-foreground">箭头</span>
        <select v-model="selectedEdgeMarker" class="h-7 rounded-md border bg-background px-2 text-xs">
          <option value="left">左箭头</option>
          <option value="right">右箭头</option>
          <option value="both">双侧箭头</option>
          <option value="none">无</option>
        </select>
        <div class="ml-1 flex items-center gap-1.5">
          <input id="edgeAnimated" v-model="selectedEdgeAnimated" type="checkbox" />
          <label for="edgeAnimated" class="text-muted-foreground">动画</label>
        </div>
      </div>

      <div v-else class="h-full" aria-hidden="true" />
    </div>

    <div class="h-[62vh] min-h-[420px] overflow-hidden rounded-md border">
      <VueFlow
        :nodes="nodes"
        :edges="edges"
        :connection-mode="connectionMode"
        :node-types="nodeTypes"
        :default-viewport="viewport"
        :fit-view-on-init="true"
        :nodes-draggable="!readonly"
        :nodes-connectable="!readonly"
        :elements-selectable="!readonly"
        :edges-updatable="!readonly"
        :zoom-on-pinch="true"
        :zoom-on-scroll="true"
        :pan-on-drag="true"
        :class="['topology-flow bg-muted/30', readonly ? 'topology-flow-readonly' : '']"
        @connect="onConnect"
        @node-click="onNodeClick"
        @node-drag-start="onNodeDragStart"
        @node-drag-stop="onNodeDragStop"
        @edge-click="onEdgeClick"
        @pane-click="clearSelection"
        @nodes-change="onNodesChange"
        @edges-change="onEdgesChange"
        @move-end="onMoveEnd"
      >
        <Background />
        <MiniMap />
        <Controls v-if="!readonly" />
      </VueFlow>
    </div>
  </div>
</template>

<script setup>
import { computed, markRaw, ref, watch } from "vue";
import { addEdge, applyEdgeChanges, applyNodeChanges, ConnectionMode, useVueFlow, VueFlow } from "@vue-flow/core";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import { MiniMap } from "@vue-flow/minimap";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Combobox } from "../ui/combobox";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../ui/dropdown-menu";
import Switch from "../ui/switch/Switch.vue";
import EditableNode from "./EditableNode.vue";
import GroupNode from "./GroupNode.vue";
import { TOPOLOGY_ICON_OPTIONS } from "./icon-options";
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";
import "@vue-flow/node-resizer/dist/style.css";

const props = defineProps({
  modelValue: { type: String, default: "" },
  readonly: { type: Boolean, default: false },
  systemOptions: { type: Array, default: () => [] },
});

const emit = defineEmits(["update:modelValue"]);

const nodes = ref([]);
const edges = ref([]);
const nodeTypes = {
  editable: markRaw(EditableNode),
  group: markRaw(GroupNode),
};
const viewport = ref({ x: 0, y: 0, zoom: 1 });
const selectedNodeId = ref(null);
const selectedEdgeId = ref(null);
const syncFromProps = ref(false);
const isDraggingNode = ref(false);
const localSerialized = ref("");
const constrainToGroup = ref(true);
const newNodeGroupId = ref("__none__");
const { toObject } = useVueFlow();
const connectionMode = ConnectionMode.Loose;
const GROUP_PADDING = 20;
const GROUP_MIN_WIDTH = 220;
const GROUP_MIN_HEIGHT = 140;
const clampNumber = (value, min, max, fallback) => Math.min(max, Math.max(min, parseSize(value, fallback)));
const parseSize = (value, fallback = 0) => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = parseFloat(String(value ?? "").trim());
  return Number.isFinite(parsed) ? parsed : fallback;
};

const normalizeNodes = (sourceNodes) => {
  if (!Array.isArray(sourceNodes)) return [];
  return sourceNodes.map((node, index) => {
    const data = { ...(node?.data || {}) };
    const isTextNode = String(data.nodeKind || "") === "text";
    data.hideHandles = !!props.readonly || isTextNode;
    const position = {
      x: parseSize(node?.position?.x, 0),
      y: parseSize(node?.position?.y, 0),
    };
    const fallbackLabel = String(node?.label || "").trim();
    if (!String(data.label || "").trim() && fallbackLabel) {
      data.label = fallbackLabel;
    }
    if (data.textAlign !== "left" && data.textAlign !== "right" && data.textAlign !== "center") {
      data.textAlign = isTextNode ? "left" : "center";
    }
    if (data.verticalAlign !== "top" && data.verticalAlign !== "bottom" && data.verticalAlign !== "center") {
      data.verticalAlign = "center";
    }
    data.fontSize = clampNumber(data.fontSize, 10, 40, 14);
    if (node?.type === "group") {
      const width = Math.max(120, parseSize(node?.style?.width, parseSize(node?.width, 280)));
      const height = Math.max(80, parseSize(node?.style?.height, parseSize(node?.height, 180)));
      const borderRadius = Math.min(80, Math.max(0, parseSize(data.borderRadius, parseSize(node?.style?.borderRadius, 12))));
      data.manualWidth = Math.max(120, parseSize(data.manualWidth, width));
      data.manualHeight = Math.max(80, parseSize(data.manualHeight, height));
      data.borderRadius = borderRadius;
      return {
        ...node,
        data,
        zIndex: 0,
        position,
        width,
        height,
        dimensions: { width, height },
        style: {
          ...(node?.style || {}),
          width: `${width}px`,
          height: `${height}px`,
          borderRadius: `${borderRadius}px`,
        },
      };
    }
    if (isTextNode) {
      data.width = clampNumber(data.width, 120, 720, 360);
      data.height = clampNumber(data.height, 20, 260, 20);
      data.borderRadius = 0;
    } else {
      data.width = clampNumber(data.width, 80, 420, 120);
      data.height = clampNumber(data.height, 40, 260, 48);
      data.borderRadius = clampNumber(data.borderRadius, 0, 60, 10);
    }
    return { ...node, data, position, connectable: isTextNode ? false : node?.connectable };
  });
};

const parseTopology = (raw) => {
  if (!raw) return { nodes: [], edges: [], viewport: { x: 0, y: 0, zoom: 1 }, options: { constrainToGroup: true } };
  try {
    const obj = typeof raw === "string" ? JSON.parse(raw) : raw;
    const normalizedNodes = normalizeNodes(Array.isArray(obj?.nodes) ? obj.nodes : []);
    const nodeIds = new Set(normalizedNodes.map((node) => String(node.id)));
    const normalizedEdges = (Array.isArray(obj?.edges) ? obj.edges : [])
      .filter((edge) => edge?.source && edge?.target && nodeIds.has(String(edge.source)) && nodeIds.has(String(edge.target)))
      .map((edge) => ({
        ...edge,
        style: {
          ...(edge?.style || {}),
          strokeWidth: clampNumber(edge?.style?.strokeWidth, 1, 12, 2),
        },
      }));
    return {
      nodes: normalizedNodes,
      edges: normalizedEdges,
      viewport: obj?.viewport && typeof obj.viewport === "object" ? obj.viewport : { x: 0, y: 0, zoom: 1 },
      options: {
        constrainToGroup: obj?.options?.constrainToGroup === undefined ? true : Boolean(obj?.options?.constrainToGroup),
      },
    };
  } catch {
    return { nodes: [], edges: [], viewport: { x: 0, y: 0, zoom: 1 }, options: { constrainToGroup: true } };
  }
};

const normalizeGroupedNodesInList = (sourceNodes) => {
  const list = Array.isArray(sourceNodes) ? sourceNodes.map((n) => ({ ...n })) : [];
  const map = new Map(list.map((node) => [node.id, node]));
  const getSize = (node) => {
    if (!node) return { width: 120, height: 48 };
    if (node.type === "group") {
      return {
        width: Math.max(120, parseSize(node?.style?.width, 280)),
        height: Math.max(80, parseSize(node?.style?.height, 180)),
      };
    }
    return {
      width: Math.max(80, parseSize(node?.data?.width, 120)),
      height: Math.max(40, parseSize(node?.data?.height, 48)),
    };
  };

  for (const node of list) {
    if (!node?.parentNode) continue;
    const parent = map.get(node.parentNode);
    if (!parent) continue;
    const parentSize = getSize(parent);
    const childSize = getSize(node);
    const maxX = Math.max(0, parentSize.width - childSize.width);
    const maxY = Math.max(0, parentSize.height - childSize.height);
    const px = parseSize(node.position?.x, 0);
    const py = parseSize(node.position?.y, 0);
    node.position = {
      x: Math.min(maxX, Math.max(0, px)),
      y: Math.min(maxY, Math.max(0, py)),
    };
    node.extent = "parent";
  }
  return list;
};

const serializeTopology = () => {
  try {
    const obj = toObject();
    return JSON.stringify({
      nodes: Array.isArray(obj?.nodes) ? obj.nodes : nodes.value,
      edges: Array.isArray(obj?.edges) ? obj.edges : edges.value,
      viewport: obj?.viewport && typeof obj.viewport === "object" ? obj.viewport : viewport.value,
      options: {
        constrainToGroup: Boolean(constrainToGroup.value),
      },
    });
  } catch {
    return JSON.stringify({
      nodes: nodes.value,
      edges: edges.value,
      viewport: viewport.value,
      options: {
        constrainToGroup: Boolean(constrainToGroup.value),
      },
    });
  }
};

const syncGraphFromFlow = () => {
  try {
    const obj = toObject();
    if (Array.isArray(obj?.nodes)) nodes.value = obj.nodes;
    if (Array.isArray(obj?.edges)) edges.value = obj.edges;
    if (obj?.viewport && typeof obj.viewport === "object") viewport.value = obj.viewport;
  } catch {
    // ignore sync failures and keep current local state
  }
};

const emitModel = () => {
  if (props.readonly || syncFromProps.value || isDraggingNode.value) return;
  const next = serializeTopology();
  if (next === localSerialized.value) return;
  localSerialized.value = next;
  emit("update:modelValue", next);
};

const loadFromModel = (raw) => {
  const normalized =
    typeof raw === "string" ? raw : raw ? JSON.stringify(raw) : "";
  if (normalized === localSerialized.value) return;
  syncFromProps.value = true;
  const parsed = parseTopology(raw);
  nodes.value = normalizeGroupedNodesInList(parsed.nodes);
  edges.value = parsed.edges;
  viewport.value = parsed.viewport;
  constrainToGroup.value = Boolean(parsed.options?.constrainToGroup);
  localSerialized.value = serializeTopology();
  selectedNodeId.value = null;
  syncFromProps.value = false;
};

watch(
  () => props.modelValue,
  (val) => loadFromModel(val),
  { immediate: true }
);

watch(
  [nodes, edges],
  () => emitModel(),
  { deep: true }
);

watch(
  viewport,
  () => emitModel(),
  { deep: true }
);

const selectedNode = computed(() => nodes.value.find((item) => item.id === selectedNodeId.value) || null);
const selectedEdge = computed(() => edges.value.find((item) => item.id === selectedEdgeId.value) || null);
const selectedNodeIsText = computed(() => String(selectedNode.value?.data?.nodeKind || "") === "text");
const selectedNodeIsSystem = computed(() => String(selectedNode.value?.data?.nodeKind || "") === "system");
const groupNodes = computed(() => nodes.value.filter((item) => item.type === "group"));
const groupOptionsWithNone = computed(() => {
  const base = [{ label: "不分组", value: "__none__" }];
  const groups = groupNodes.value.map((item) => ({
    label: String(item?.data?.label || item.id),
    value: String(item.id),
  }));
  return [...base, ...groups];
});
const systemNodeOptions = computed(() => {
  const base = [{ label: "选择系统", value: "__none__" }];
  const items = Array.isArray(props.systemOptions) ? props.systemOptions : [];
  const normalized = items
    .filter((item) => item && item.value !== null && item.value !== undefined && String(item.value).trim() !== "")
    .map((item) => ({
      value: String(item.value),
      label: String(item.label ?? item.value),
    }));
  return [...base, ...normalized];
});
const systemNodeKeyword = ref("");
const filteredSystemNodeItems = computed(() => {
  const items = systemNodeOptions.value.filter((item) => item.value !== "__none__");
  const keyword = systemNodeKeyword.value.trim().toLowerCase();
  if (!keyword) return items;
  return items.filter((item) => String(item.label).toLowerCase().includes(keyword) || String(item.value).toLowerCase().includes(keyword));
});

const getNodeMap = () => new Map(nodes.value.map((node) => [node.id, node]));

const getNodeAbsolutePosition = (node, map, depth = 0) => {
  if (!node || depth > 16) return { x: 0, y: 0 };
  const current = node.position || { x: 0, y: 0 };
  if (!node.parentNode) return { x: Number(current.x || 0), y: Number(current.y || 0) };
  const parent = map.get(node.parentNode);
  if (!parent) return { x: Number(current.x || 0), y: Number(current.y || 0) };
  const parentAbs = getNodeAbsolutePosition(parent, map, depth + 1);
  return {
    x: parentAbs.x + Number(current.x || 0),
    y: parentAbs.y + Number(current.y || 0),
  };
};

const getNodeSize = (node) => {
  if (!node) return { width: 120, height: 48 };
  if (node.type === "group") {
    const styleWidth = parseSize(node?.style?.width, 0);
    const styleHeight = parseSize(node?.style?.height, 0);
    const dimensionWidth = parseSize(node?.dimensions?.width ?? node?.width, 0);
    const dimensionHeight = parseSize(node?.dimensions?.height ?? node?.height, 0);
    return {
      width: Math.max(120, styleWidth || dimensionWidth || 280),
      height: Math.max(80, styleHeight || dimensionHeight || 180),
    };
  }
  return {
    width: Math.max(80, Number(node?.data?.width || 120)),
    height: Math.max(40, Number(node?.data?.height || 48)),
  };
};

const clampGroupedNodePosition = (node, map) => {
  if (!node?.parentNode) return node;
  const parent = map.get(node.parentNode);
  if (!parent) return node;
  const parentSize = getNodeSize(parent);
  const childSize = getNodeSize(node);
  const maxX = Math.max(0, parentSize.width - childSize.width);
  const maxY = Math.max(0, parentSize.height - childSize.height);
  const px = Number(node.position?.x || 0);
  const py = Number(node.position?.y || 0);
  const nx = Math.min(maxX, Math.max(0, px));
  const ny = Math.min(maxY, Math.max(0, py));
  if (nx === px && ny === py) return node;
  return { ...node, position: { x: nx, y: ny } };
};

const normalizeGroupedNodePositions = () => {
  const map = getNodeMap();
  nodes.value = nodes.value.map((node) => clampGroupedNodePosition(node, map));
};

const findGroupAtPoint = (point, excludeNodeId = "") => {
  const map = getNodeMap();
  const candidates = groupNodes.value
    .filter((group) => group.id !== excludeNodeId)
    .map((group) => {
      const abs = getNodeAbsolutePosition(group, map);
      const size = getNodeSize(group);
      return { group, abs, size, area: size.width * size.height };
    })
    .filter(({ abs, size }) => point.x >= abs.x && point.x <= abs.x + size.width && point.y >= abs.y && point.y <= abs.y + size.height)
    .sort((a, b) => a.area - b.area);
  return candidates[0]?.group || null;
};

const withGroupConstraint = (node) => {
  if (!node) return node;
  if (!node.parentNode) {
    const next = { ...node };
    delete next.extent;
    return next;
  }
  if (!constrainToGroup.value) {
    const next = { ...node };
    delete next.extent;
    return next;
  }
  return { ...node, extent: "parent" };
};

const getNodeDepth = (node, map, seen = new Set()) => {
  if (!node?.parentNode) return 0;
  if (seen.has(node.id)) return 0;
  const parent = map.get(node.parentNode);
  if (!parent) return 0;
  const nextSeen = new Set(seen);
  nextSeen.add(node.id);
  return 1 + getNodeDepth(parent, map, nextSeen);
};

const fitGroupToChildren = (groupId) => {
  const map = new Map(nodes.value.map((node) => [node.id, node]));
  const group = map.get(groupId);
  if (!group || group.type !== "group") return;

  const children = nodes.value.filter((node) => node.parentNode === groupId);
  if (!children.length) return;

  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;

  for (const child of children) {
    const abs = getNodeAbsolutePosition(child, map);
    const size = getNodeSize(child);
    minX = Math.min(minX, abs.x);
    minY = Math.min(minY, abs.y);
    maxX = Math.max(maxX, abs.x + size.width);
    maxY = Math.max(maxY, abs.y + size.height);
  }

  const manualWidth = parseSize(group?.data?.manualWidth, 0);
  const manualHeight = parseSize(group?.data?.manualHeight, 0);
  const hasManualWidth = manualWidth > 0;
  const hasManualHeight = manualHeight > 0;

  const currentAbs = getNodeAbsolutePosition(group, map);
  const autoAbsX = minX - GROUP_PADDING;
  const autoAbsY = minY - GROUP_PADDING;
  const autoWidth = Math.max(GROUP_MIN_WIDTH, Math.ceil(maxX - minX + GROUP_PADDING * 2));
  const autoHeight = Math.max(GROUP_MIN_HEIGHT, Math.ceil(maxY - minY + GROUP_PADDING * 2));

  // Manual size has priority and should not be overridden by auto-fit.
  const desiredAbsX = hasManualWidth ? currentAbs.x : autoAbsX;
  const desiredAbsY = hasManualHeight ? currentAbs.y : autoAbsY;
  const desiredWidth = hasManualWidth ? Math.max(GROUP_MIN_WIDTH, manualWidth) : autoWidth;
  const desiredHeight = hasManualHeight ? Math.max(GROUP_MIN_HEIGHT, manualHeight) : autoHeight;
  const parent = group.parentNode ? map.get(group.parentNode) : null;
  const parentAbs = parent ? getNodeAbsolutePosition(parent, map) : { x: 0, y: 0 };
  const nextGroupPos = group.parentNode
    ? { x: desiredAbsX - parentAbs.x, y: desiredAbsY - parentAbs.y }
    : { x: desiredAbsX, y: desiredAbsY };

  nodes.value = nodes.value.map((node) => {
    if (node.id === groupId) {
      return {
        ...node,
        zIndex: 0,
        width: desiredWidth,
        height: desiredHeight,
        dimensions: { width: desiredWidth, height: desiredHeight },
        position: nextGroupPos,
        style: {
          ...(node.style || {}),
          width: `${desiredWidth}px`,
          height: `${desiredHeight}px`,
        },
      };
    }
    if (node.parentNode !== groupId) return node;
    const abs = getNodeAbsolutePosition(node, map);
    const next = {
      ...node,
      position: {
        x: abs.x - desiredAbsX,
        y: abs.y - desiredAbsY,
      },
    };
    return withGroupConstraint(next);
  });
};

const autoExpandGroups = () => {
  const map = getNodeMap();
  const groupIds = nodes.value
    .filter((node) => node.type === "group")
    .map((node) => ({ id: node.id, depth: getNodeDepth(node, map) }))
    .sort((a, b) => b.depth - a.depth)
    .map((item) => item.id);

  for (const groupId of groupIds) {
    fitGroupToChildren(groupId);
  }
  if (constrainToGroup.value) {
    normalizeGroupedNodePositions();
  }
};

const reparentNode = (nodeId, targetGroupId = null) => {
  const map = getNodeMap();
  const node = map.get(nodeId);
  if (!node || node.type === "group") return;
  const nodeAbs = getNodeAbsolutePosition(node, map);
  const nextNodes = nodes.value.map((item) => {
    if (item.id !== nodeId) return item;
    const next = { ...item };
    if (!targetGroupId || targetGroupId === "__none__") {
      next.position = { x: nodeAbs.x, y: nodeAbs.y };
      delete next.parentNode;
      delete next.extent;
      return next;
    }
    const group = map.get(targetGroupId);
    if (!group || group.type !== "group") return next;
    const groupAbs = getNodeAbsolutePosition(group, map);
    next.parentNode = targetGroupId;
    next.position = {
      x: nodeAbs.x - groupAbs.x,
      y: nodeAbs.y - groupAbs.y,
    };
    return withGroupConstraint(next);
  });
  nodes.value = nextNodes;
  autoExpandGroups();
};

const updateEdgeById = (edgeId, updater) => {
  syncGraphFromFlow();
  edges.value = edges.value.map((edge) => {
    if (edge.id !== edgeId) return edge;
    const next = updater(edge);
    return next || edge;
  });
};

const selectedNodeLabel = computed({
  get() {
    return selectedNode.value?.data?.label || "";
  },
  set(value) {
    if (!selectedNode.value) return;
    if (String(selectedNode.value?.data?.nodeKind || "") === "system") return;
    const nodeId = selectedNode.value.id;
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), label: value } } : n
    );
  },
});

const selectedNodeIcon = computed({
  get: () => selectedNode.value?.data?.icon || "__none__",
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    const icon = value === "__none__" ? "" : String(value || "").trim();
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), icon } } : n
    );
  },
});
const selectedNodeBgColor = computed({
  get: () => selectedNode.value?.data?.bgColor || "#ffffff",
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), bgColor: value } } : n
    );
  },
});
const selectedNodeBorderColor = computed({
  get: () => selectedNode.value?.data?.borderColor || "#cbd5e1",
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), borderColor: value } } : n
    );
  },
});
const selectedNodeTextColor = computed({
  get: () => selectedNode.value?.data?.textColor || "#0f172a",
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), textColor: value } } : n
    );
  },
});
const selectedNodeWidth = computed({
  get: () => clampNumber(selectedNode.value?.data?.width, 80, 420, 120),
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    const width = clampNumber(value, 80, 420, 120);
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), width } } : n
    );
    normalizeGroupedNodePositions();
  },
});
const selectedNodeHeight = computed({
  get: () => clampNumber(selectedNode.value?.data?.height, 40, 260, 48),
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    const height = clampNumber(value, 40, 260, 48);
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), height } } : n
    );
    normalizeGroupedNodePositions();
  },
});
const selectedNodeRadius = computed({
  get: () => clampNumber(selectedNode.value?.data?.borderRadius, 0, 60, 10),
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    const borderRadius = clampNumber(value, 0, 60, 10);
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), borderRadius } } : n
    );
  },
});
const selectedNodeFontSize = computed({
  get: () => clampNumber(selectedNode.value?.data?.fontSize, 10, 40, 14),
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    const fontSize = clampNumber(value, 10, 40, 14);
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), fontSize } } : n
    );
  },
});
const selectedNodeTextAlign = computed({
  get: () => {
    const align = String(selectedNode.value?.data?.textAlign || "center");
    return align === "left" || align === "right" ? align : "center";
  },
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    const textAlign = value === "left" || value === "right" ? value : "center";
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), textAlign } } : n
    );
  },
});
const selectedNodeVerticalAlign = computed({
  get: () => {
    const align = String(selectedNode.value?.data?.verticalAlign || "center");
    return align === "top" || align === "bottom" ? align : "center";
  },
  set: (value) => {
    if (!selectedNode.value) return;
    const nodeId = selectedNode.value.id;
    const verticalAlign = value === "top" || value === "bottom" ? value : "center";
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId ? { ...n, data: { ...(n.data || {}), verticalAlign } } : n
    );
  },
});

const selectedNodeGroupId = computed({
  get: () => String(selectedNode.value?.parentNode || "__none__"),
  set: (value) => {
    if (!selectedNode.value || selectedNode.value.type === "group") return;
    reparentNode(selectedNode.value.id, value === "__none__" ? null : value);
  },
});

const selectedGroupWidth = computed({
  get: () => parseSize(selectedNode.value?.data?.manualWidth, parseSize(selectedNode.value?.style?.width, 280)),
  set: (value) => {
    if (!selectedNode.value || selectedNode.value.type !== "group") return;
    const nodeId = selectedNode.value.id;
    const width = clampNumber(value, 120, 1200, 280);
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId
        ? {
            ...n,
            width,
            // Keep the other axis stable when changing width.
            height: parseSize(n.height ?? n?.style?.height, 180),
            dimensions: { width, height: parseSize(n.height ?? n?.style?.height, 180) },
            data: { ...(n.data || {}), manualWidth: width },
            style: { ...(n.style || {}), width: `${width}px` },
          }
        : n
    );
    autoExpandGroups();
  },
});

const selectedGroupHeight = computed({
  get: () => parseSize(selectedNode.value?.data?.manualHeight, parseSize(selectedNode.value?.style?.height, 180)),
  set: (value) => {
    if (!selectedNode.value || selectedNode.value.type !== "group") return;
    const nodeId = selectedNode.value.id;
    const height = clampNumber(value, 80, 1000, 180);
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId
        ? {
            ...n,
            // Keep the other axis stable when changing height.
            width: parseSize(n.width ?? n?.style?.width, 280),
            height,
            dimensions: { width: parseSize(n.width ?? n?.style?.width, 280), height },
            data: { ...(n.data || {}), manualHeight: height },
            style: { ...(n.style || {}), height: `${height}px` },
          }
        : n
    );
    autoExpandGroups();
  },
});

const selectedGroupRadius = computed({
  get: () => {
    const fromData = parseSize(selectedNode.value?.data?.borderRadius, 0);
    if (fromData > 0 || fromData === 0) return Math.max(0, Math.min(60, fromData));
    const fromStyle = parseSize(selectedNode.value?.style?.borderRadius, 12);
    return Math.max(0, Math.min(60, fromStyle));
  },
  set: (value) => {
    if (!selectedNode.value || selectedNode.value.type !== "group") return;
    const nodeId = selectedNode.value.id;
    const borderRadius = clampNumber(value, 0, 80, 12);
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId
        ? {
            ...n,
            data: { ...(n.data || {}), borderRadius },
            style: { ...(n.style || {}), borderRadius: `${borderRadius}px` },
          }
        : n
    );
  },
});

const selectedGroupBgColor = computed({
  get: () => {
    const raw = String(selectedNode.value?.style?.backgroundColor || "").trim();
    const hex = /^#([0-9a-fA-F]{6})$/.test(raw) ? raw : "";
    return hex || "#e2e8f0";
  },
  set: (value) => {
    if (!selectedNode.value || selectedNode.value.type !== "group") return;
    const nodeId = selectedNode.value.id;
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) =>
      n.id === nodeId
        ? { ...n, data: { ...(n.data || {}), bgColor: value }, style: { ...(n.style || {}), backgroundColor: value } }
        : n
    );
  },
});

const selectedGroupBorderColor = computed({
  get: () => {
    const border = String(selectedNode.value?.style?.border || "");
    const color = border.split(" ").at(-1);
    return color && color.startsWith("#") ? color : "#cbd5e1";
  },
  set: (value) => {
    if (!selectedNode.value || selectedNode.value.type !== "group") return;
    const nodeId = selectedNode.value.id;
    syncGraphFromFlow();
    nodes.value = nodes.value.map((n) => {
      if (n.id !== nodeId) return n;
      const prev = String(n.style?.border || "1px dashed #cbd5e1");
      const segments = prev.split(" ");
      const width = segments[0] || "1px";
      const line = segments[1] || "dashed";
      return {
        ...n,
        data: { ...(n.data || {}), borderColor: value },
        style: { ...(n.style || {}), border: `${width} ${line} ${value}` },
      };
    });
  },
});

const moveSelectedNodeToGroup = () => {
  if (!selectedNode.value || selectedNode.value.type === "group") return;
  if (!selectedNodeGroupId.value || selectedNodeGroupId.value === "__none__") return;
  reparentNode(selectedNode.value.id, selectedNodeGroupId.value);
};

const removeSelectedNodeFromGroup = () => {
  if (!selectedNode.value || selectedNode.value.type === "group") return;
  reparentNode(selectedNode.value.id, null);
};

watch(constrainToGroup, () => {
  nodes.value = nodes.value.map((node) => withGroupConstraint(node));
  autoExpandGroups();
  emitModel();
});

watch(groupOptionsWithNone, (options) => {
  const valid = new Set(options.map((item) => item.value));
  if (!valid.has(newNodeGroupId.value)) {
    newNodeGroupId.value = "__none__";
  }
}, { deep: true });

const selectedEdgeColor = computed({
  get: () => selectedEdge.value?.style?.stroke || "#334155",
  set: (value) => {
    if (!selectedEdge.value) return;
    const edgeId = selectedEdge.value.id;
    updateEdgeById(edgeId, (edge) => ({
      ...edge,
      style: { ...(edge.style || {}), stroke: value },
    }));
  },
});
const selectedEdgeWidth = computed({
  get: () => clampNumber(selectedEdge.value?.style?.strokeWidth, 1, 12, 2),
  set: (value) => {
    if (!selectedEdge.value) return;
    const edgeId = selectedEdge.value.id;
    updateEdgeById(edgeId, (edge) => ({
      ...edge,
      style: { ...(edge.style || {}), strokeWidth: clampNumber(value, 1, 12, 2) },
    }));
  },
});
const selectedEdgeLineType = computed({
  get: () => {
    const dash = String(selectedEdge.value?.style?.strokeDasharray || "").trim();
    if (!dash) return "solid";
    if (dash === "6 4") return "dashed";
    if (dash === "2 4") return "dotted";
    if (dash === "8 4 2 4") return "dashdot";
    return "dashed";
  },
  set: (value) => {
    if (!selectedEdge.value) return;
    const edgeId = selectedEdge.value.id;
    updateEdgeById(edgeId, (edge) => {
      const style = { ...(edge.style || {}) };
      if (value === "dashed") style.strokeDasharray = "6 4";
      else if (value === "dotted") style.strokeDasharray = "2 4";
      else if (value === "dashdot") style.strokeDasharray = "8 4 2 4";
      else delete style.strokeDasharray;
      return { ...edge, style };
    });
  },
});
const selectedEdgePathType = computed({
  get: () => {
    const edgeType = String(selectedEdge.value?.type || "default");
    if (edgeType === "smoothstep" || edgeType === "step" || edgeType === "straight") return edgeType;
    return "default";
  },
  set: (value) => {
    if (!selectedEdge.value) return;
    const edgeId = selectedEdge.value.id;
    updateEdgeById(edgeId, (edge) => ({ ...edge, type: value || "default" }));
  },
});
const selectedEdgeAnimated = computed({
  get: () => Boolean(selectedEdge.value?.animated),
  set: (value) => {
    if (!selectedEdge.value) return;
    const edgeId = selectedEdge.value.id;
    updateEdgeById(edgeId, (edge) => ({ ...edge, animated: Boolean(value) }));
  },
});
const selectedEdgeMarker = computed({
  get: () => {
    const start = selectedEdge.value?.markerStart;
    const end = selectedEdge.value?.markerEnd;
    const isArrow = (marker) => {
      if (!marker) return false;
      if (typeof marker === "string") return marker.toLowerCase().includes("arrow");
      if (typeof marker === "object" && marker.type) return String(marker.type).toLowerCase().includes("arrow");
      return false;
    };
    const hasStart = isArrow(start);
    const hasEnd = isArrow(end);
    if (hasStart && hasEnd) return "both";
    if (hasStart) return "left";
    if (hasEnd) return "right";
    return "none";
  },
  set: (value) => {
    if (!selectedEdge.value) return;
    const edgeId = selectedEdge.value.id;
    updateEdgeById(edgeId, (edge) => {
      if (value === "both") {
        return { ...edge, markerStart: "arrowclosed", markerEnd: "arrowclosed" };
      }
      if (value === "left") {
        return { ...edge, markerStart: "arrowclosed", markerEnd: undefined };
      }
      if (value === "right") {
        return { ...edge, markerStart: undefined, markerEnd: "arrowclosed" };
      }
      return { ...edge, markerStart: undefined, markerEnd: undefined };
    });
  },
});

const nextNodeId = () => `n-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

const addNode = () => {
  const id = nextNodeId();
  const selectedGroup = newNodeGroupId.value !== "__none__" ? nodes.value.find((item) => item.id === newNodeGroupId.value && item.type === "group") : null;
  nodes.value = [
    ...nodes.value,
    withGroupConstraint({
      id,
      type: "editable",
      parentNode: selectedGroup ? selectedGroup.id : undefined,
      position: selectedGroup
        ? { x: 24 + ((nodes.value.length * 12) % 120), y: 24 + ((nodes.value.length * 10) % 80) }
        : { x: 120 + nodes.value.length * 30, y: 80 + nodes.value.length * 20 },
      data: {
        label: `节点 ${nodes.value.length + 1}`,
        icon: "",
        bgColor: "#ffffff",
        borderColor: "#cbd5e1",
        textColor: "#0f172a",
        width: 120,
        height: 48,
        borderRadius: 10,
        fontSize: 14,
        textAlign: "center",
        verticalAlign: "center",
      },
    }),
  ];
  if (selectedGroup) autoExpandGroups();
  selectedNodeId.value = id;
  selectedEdgeId.value = null;
};

const addTextNode = () => {
  const id = nextNodeId();
  const selectedGroup = newNodeGroupId.value !== "__none__" ? nodes.value.find((item) => item.id === newNodeGroupId.value && item.type === "group") : null;
  nodes.value = [
    ...nodes.value,
    withGroupConstraint({
      id,
      type: "editable",
      parentNode: selectedGroup ? selectedGroup.id : undefined,
      position: selectedGroup
        ? { x: 24 + ((nodes.value.length * 12) % 120), y: 24 + ((nodes.value.length * 10) % 80) }
        : { x: 120 + nodes.value.length * 30, y: 80 + nodes.value.length * 20 },
      data: {
        label: "请输入注释",
        nodeKind: "text",
        icon: "",
        hideHandles: true,
        bgColor: "transparent",
        borderColor: "transparent",
        textColor: "#334155",
        width: 360,
        height: 20,
        borderRadius: 0,
        fontSize: 12,
        textAlign: "left",
        verticalAlign: "top",
      },
      connectable: false,
    }),
  ];
  if (selectedGroup) autoExpandGroups();
  selectedNodeId.value = id;
  selectedEdgeId.value = null;
};

const addSystemNode = (systemId) => {
  if (!systemId || systemId === "__none__") return;
  const option = systemNodeOptions.value.find((item) => item.value === systemId);
  if (!option) return;
  const id = nextNodeId();
  const selectedGroup = newNodeGroupId.value !== "__none__" ? nodes.value.find((item) => item.id === newNodeGroupId.value && item.type === "group") : null;
  nodes.value = [
    ...nodes.value,
    withGroupConstraint({
      id,
      type: "editable",
      parentNode: selectedGroup ? selectedGroup.id : undefined,
      position: selectedGroup
        ? { x: 24 + ((nodes.value.length * 12) % 120), y: 24 + ((nodes.value.length * 10) % 80) }
        : { x: 120 + nodes.value.length * 30, y: 80 + nodes.value.length * 20 },
      data: {
        label: option.label,
        systemId: option.value,
        nodeKind: "system",
        icon: "server",
        bgColor: "#ecfdf5",
        borderColor: "#10b981",
        textColor: "#065f46",
        width: 160,
        height: 52,
        borderRadius: 10,
        fontSize: 14,
        textAlign: "center",
        verticalAlign: "center",
      },
    }),
  ];
  if (selectedGroup) autoExpandGroups();
  selectedNodeId.value = id;
  selectedEdgeId.value = null;
  systemNodeKeyword.value = "";
};

const addGroup = () => {
  const id = nextNodeId();
  const width = 280;
  const height = 180;
  nodes.value = [
    ...nodes.value,
    {
      id,
      type: "group",
      zIndex: 0,
      width,
      height,
      dimensions: { width, height },
      position: { x: 80 + nodes.value.length * 20, y: 60 + nodes.value.length * 20 },
      data: {
        label: `分组 ${nodes.value.length + 1}`,
        manualWidth: width,
        manualHeight: height,
        borderRadius: 12,
        bgColor: "#e2e8f0",
        borderColor: "#cbd5e1",
      },
      style: {
        width: `${width}px`,
        height: `${height}px`,
        borderRadius: "12px",
        backgroundColor: "#e2e8f0",
        border: "1px dashed #cbd5e1",
      },
    },
  ];
  selectedNodeId.value = id;
};

const removeSelectedNode = () => {
  if (!selectedNodeId.value) return;
  const removeId = selectedNodeId.value;
  const removing = nodes.value.find((node) => node.id === removeId);
  const map = getNodeMap();
  if (removing?.type === "group") {
    const groupAbs = getNodeAbsolutePosition(removing, map);
    nodes.value = nodes.value
      .filter((node) => node.id !== removeId)
      .map((node) => {
        if (node.parentNode !== removeId) return node;
        const childAbs = getNodeAbsolutePosition(node, map);
        return {
          ...node,
          position: { x: childAbs.x, y: childAbs.y },
          parentNode: undefined,
          extent: undefined,
        };
      });
  } else {
    nodes.value = nodes.value.filter((node) => node.id !== removeId);
  }
  edges.value = edges.value.filter((edge) => edge.source !== removeId && edge.target !== removeId);
  autoExpandGroups();
  selectedNodeId.value = null;
};

const removeSelectedEdge = () => {
  if (!selectedEdgeId.value) return;
  edges.value = edges.value.filter((edge) => edge.id !== selectedEdgeId.value);
  selectedEdgeId.value = null;
};

const removeSelected = () => {
  if (selectedNodeId.value) {
    removeSelectedNode();
    return;
  }
  if (selectedEdgeId.value) {
    removeSelectedEdge();
  }
};

const onConnect = (params) => {
  if (props.readonly) return;
  const sourceNode = nodes.value.find((item) => item.id === params?.source);
  const targetNode = nodes.value.find((item) => item.id === params?.target);
  const sourceIsText = String(sourceNode?.data?.nodeKind || "") === "text";
  const targetIsText = String(targetNode?.data?.nodeKind || "") === "text";
  if (sourceIsText || targetIsText) return;
  edges.value = addEdge(
    {
      ...params,
      animated: false,
      markerEnd: "arrowclosed",
      style: { stroke: "#334155", strokeWidth: 2 },
    },
    edges.value
  );
};

const onNodesChange = (changes) => {
  nodes.value = applyNodeChanges(changes, nodes.value);

  // Persist resized width/height into node data/style so reopening keeps the exact size.
  const dimensionChanges = changes.filter((change) => change?.type === "dimensions" && change?.dimensions);
  if (!dimensionChanges.length) return;

  const dimMap = new Map(
    dimensionChanges.map((change) => [
      change.id,
      {
        width: Math.round(Number(change.dimensions.width || 0)),
        height: Math.round(Number(change.dimensions.height || 0)),
      },
    ])
  );

  nodes.value = nodes.value.map((node) => {
    const dim = dimMap.get(node.id);
    if (!dim) return node;

    if (node.type === "group") {
      const width = Math.max(120, dim.width || 280);
      const height = Math.max(80, dim.height || 180);
      return {
        ...node,
        width,
        height,
        dimensions: { width, height },
        data: { ...(node.data || {}), manualWidth: width, manualHeight: height },
        style: { ...(node.style || {}), width: `${width}px`, height: `${height}px` },
      };
    }

    const width = Math.max(80, Math.min(420, dim.width || 120));
    const height = Math.max(40, Math.min(260, dim.height || 48));
    return {
      ...node,
      dimensions: { width, height },
      data: { ...(node.data || {}), width, height },
    };
  });
};

const onEdgesChange = (changes) => {
  edges.value = applyEdgeChanges(changes, edges.value);
};

const onNodeClick = ({ node }) => {
  selectedNodeId.value = node?.id || null;
  selectedEdgeId.value = null;
};

const onNodeDragStart = () => {
  isDraggingNode.value = true;
};

const onNodeDragStop = ({ node } = {}) => {
  isDraggingNode.value = false;
  if (!node?.id) return;

  // Persist latest drag position first (Vue Flow gives relative position in parent)
  nodes.value = nodes.value.map((n) => (n.id === node.id ? { ...n, position: { ...(node.position || n.position) } } : n));

  const dragged = nodes.value.find((item) => item.id === node.id);
  if (dragged && dragged.type !== "group") {
    const map = getNodeMap();
    const abs = node.positionAbsolute || getNodeAbsolutePosition(dragged, map);
    const size = getNodeSize(dragged);
    const center = { x: Number(abs.x || 0) + size.width / 2, y: Number(abs.y || 0) + size.height / 2 };
    const targetGroup = findGroupAtPoint(center, dragged.id);

    if (targetGroup && dragged.parentNode !== targetGroup.id) {
      reparentNode(dragged.id, targetGroup.id);
    } else if (!targetGroup && dragged.parentNode && !constrainToGroup.value) {
      reparentNode(dragged.id, null);
    } else {
      // keep extent in sync with toggle even when parent unchanged
      nodes.value = nodes.value.map((n) => (n.id === dragged.id ? withGroupConstraint(n) : n));
      autoExpandGroups();
    }
  } else if (dragged?.type === "group") {
    autoExpandGroups();
  }

  emitModel();
};

const onEdgeClick = ({ edge }) => {
  selectedEdgeId.value = edge?.id || null;
  selectedNodeId.value = null;
};

const clearSelection = () => {
  selectedNodeId.value = null;
  selectedEdgeId.value = null;
};

const onMoveEnd = ({ viewport: vp }) => {
  if (vp) {
    viewport.value = vp;
    emitModel();
  }
};

const getSnapshot = () => serializeTopology();

defineExpose({
  getSnapshot,
});
</script>

<style>
.topology-flow.vue-flow .vue-flow__edge-pane,
.topology-flow.vue-flow .vue-flow__edges {
  z-index: 20 !important;
}

.topology-flow.vue-flow .vue-flow__nodes {
  z-index: 10 !important;
}

.topology-flow.vue-flow .vue-flow__node-group {
  z-index: 0 !important;
}

.topology-flow.vue-flow .vue-flow__node:not(.vue-flow__node-group) {
  z-index: 15 !important;
}

.topology-flow.vue-flow .vue-flow__edge-path {
  pointer-events: stroke;
}

.topology-flow-readonly.vue-flow .vue-flow__handle,
.topology-flow-readonly .vue-flow__handle {
  display: none;
}
</style>

