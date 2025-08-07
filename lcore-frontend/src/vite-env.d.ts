/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_WALLET_CONNECT_PROJECT_ID: string
  readonly VITE_LOCALE_NETWORK_RPC: string
  readonly VITE_CARTESI_GRAPHQL: string
  readonly VITE_INPUT_BOX_ADDRESS: string
  readonly VITE_CARTESI_DAPP_ADDRESS: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// AppKit Web Components
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'w3m-button': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    }
  }
} 