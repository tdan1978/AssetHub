import { createApp } from "vue";

const renderToString = (Component, props = {}) => {
  const container = document.createElement("div");
  const app = createApp(Component, props);
  app.mount(container);
  const html = container.innerHTML;
  app.unmount();
  return html;
};

export function componentToString(configOrComponent, componentOrProps = {}, props = {}) {
  if (typeof configOrComponent === "object" && (componentOrProps?.render || componentOrProps?.setup)) {
    const config = configOrComponent;
    const Component = componentOrProps;
    const extraProps = props || {};
    return (datum, index, data) =>
      renderToString(Component, { ...extraProps, config, payload: datum, index, data });
  }

  const Component = configOrComponent;
  const extraProps = componentOrProps || {};
  return renderToString(Component, extraProps);
}
