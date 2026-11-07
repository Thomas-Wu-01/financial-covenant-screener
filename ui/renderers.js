import { h } from "./kit/components.js";
export default { ScreenCovenantsOutput: (value) => h("p", { class: "screen", text: `${value.overall}: ${value.companies.length} company result(s)` }) };
