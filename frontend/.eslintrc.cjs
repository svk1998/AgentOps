/* eslint-env node */
'use strict'

module.exports = {
  root: true,

  env: {
    browser: true,
    es2022: true,
    node: true,
  },

  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    // Must be last — disables all ESLint rules that conflict with Prettier
    'prettier',
  ],

  plugins: ['vue'],

  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },

  rules: {
    // ── Vue: template ────────────────────────────────────────────────────────
    // Allow single-word component names (LoginView, DashboardView, etc.)
    'vue/multi-word-component-names': 'off',
    // Enforce consistent component tag order: <template> → <script> → <style>
    'vue/component-tags-order': ['error', { order: ['template', 'script', 'style'] }],
    // Require emits to be declared
    'vue/require-explicit-emits': 'error',
    // Disallow unused variables in v-for and slot scopes
    'vue/no-unused-vars': 'error',
    // No side-effects in computed properties
    'vue/no-side-effects-in-computed-properties': 'error',
    // Attribute order inside components
    'vue/attributes-order': ['warn', { alphabetical: false }],

    // ── Vue: script ──────────────────────────────────────────────────────────
    // defineProps/defineEmits must use the macro style
    'vue/define-macros-order': ['error', { order: ['defineProps', 'defineEmits'] }],

    // ── JavaScript: correctness ──────────────────────────────────────────────
    // Treat unused variables as errors, allow _-prefixed intentional ignores
    'no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    // Enforce strict equality
    eqeqeq: ['error', 'always', { null: 'ignore' }],
    // Disallow var; use const/let
    'no-var': 'error',
    // Prefer const where possible
    'prefer-const': ['error', { destructuring: 'all' }],
    // Only warn on console — useful during dev, noisy in prod
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    // Disallow duplicate imports
    'no-duplicate-imports': 'error',

    // ── JavaScript: style (non-formatting, safe alongside Prettier) ──────────
    // Require === null checks to use strict equality (covered by eqeqeq above)
    // Require object shorthand: { foo: foo } → { foo }
    'object-shorthand': ['error', 'always'],
    // Arrow functions: omit braces/return when possible
    'arrow-body-style': ['error', 'as-needed'],
  },

  ignorePatterns: ['dist/', 'coverage/', 'node_modules/'],
}
