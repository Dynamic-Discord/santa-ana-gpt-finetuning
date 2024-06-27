import globals from "globals"
import pluginJs from "@eslint/js"
import tseslint from "typescript-eslint"
import pluginReactConfig from "eslint-plugin-react/configs/recommended.js"
import { fixupConfigRules } from "@eslint/compat"


export default [
  {files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"]},
  { languageOptions: { parserOptions: { ecmaFeatures: { jsx: true } } } },
  {languageOptions: { globals: globals.browser }},
  {rules: {
    // Rule to only use arrow functions
    "prefer-arrow-callback": "error",
    // Rule to not use var
    "no-var": "error",
    "prefer-const": "error",

    // Rule to not use semicolons
    "semi": ["error", "never"],
    // Limit line length to 120 characters
    "max-len": ["error", { "code": 120 }],
   }},
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  ...fixupConfigRules(pluginReactConfig),
]