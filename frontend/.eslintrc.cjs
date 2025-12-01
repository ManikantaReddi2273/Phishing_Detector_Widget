module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2021: true
  },
  extends: [
    "eslint:recommended",
    "plugin:react-hooks/recommended",
    "eslint-config-prettier"
  ],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module"
  },
  rules: {
    "react-refresh/only-export-components": "warn"
  },
  plugins: ["react-refresh"]
};

