// AppKit Wallet Configuration for L{CORE}
import { createAppKit } from '@reown/appkit/react'
import { WagmiAdapter } from '@reown/appkit-adapter-wagmi'
import { localeNetwork } from './networks.js'
import { QueryClient } from '@tanstack/react-query'

// Get project ID from environment
const projectId = import.meta.env.VITE_WALLET_CONNECT_PROJECT_ID

if (!projectId) {
  console.warn('VITE_WALLET_CONNECT_PROJECT_ID not set. Wallet functionality will be limited.')
}

// Create wagmi adapter
const wagmiAdapter = new WagmiAdapter({
  ssr: true,
  networks: [localeNetwork],
  projectId: projectId || 'demo-project-id'
})

// Create the modal
export const modal = createAppKit({
  adapters: [wagmiAdapter],
  networks: [localeNetwork],
  projectId: projectId || 'demo-project-id',
  metadata: {
    name: 'L{CORE} IoT Dashboard',
    description: 'Privacy-preserving IoT data marketplace',
    url: window.location.origin,
    icons: [`${window.location.origin}/Locale Logo.png`]
  },
  themeMode: 'light',
  themeVariables: {
    '--w3m-accent': '#3b82f6', // Locale blue
    '--w3m-border-radius-master': '8px',
    '--w3m-font-family': 'Inter, system-ui, sans-serif'
  },
  featuredWalletIds: [
    'c57ca95b47569778a828d19178114f4db188b89b763c899ba0be274e97267d96', // MetaMask
    '1ae92b26df02f0abca6304df07debccd18262fdf5fe82daa81593582dac9a369', // Rainbow
    'fd20dc426fb37566d803205b19bbc1d4096b248ac04548e3cfb6b3a38bd033aa'  // Coinbase Wallet
  ],
  includeWalletIds: [
    'c57ca95b47569778a828d19178114f4db188b89b763c899ba0be274e97267d96', // MetaMask
    '1ae92b26df02f0abca6304df07debccd18262fdf5fe82daa81593582dac9a369', // Rainbow
    'fd20dc426fb37566d803205b19bbc1d4096b248ac04548e3cfb6b3a38bd033aa', // Coinbase Wallet
    '4622a2b2d6af1c9844944291e5e7351a6aa24cd7b23099efac1b2fd875da31a0', // Trust Wallet
    'c03dfee351b6fcc421b4494ea33b9d4b92a984f87aa76d1663bb28705e95034a'  // Uniswap Wallet
  ],
  enableWallets: true
})

export const queryClient = new QueryClient()
export const wagmiConfig = wagmiAdapter.wagmiConfig

// Whitelist for IoT simulator control
export const SIMULATOR_ADMIN_WALLETS = [
  '0x0a9871196E546a277072a04a6E1C1bC2CC25aaA2', // Primary admin wallet
  // Add more admin wallets as needed
].map(addr => addr.toLowerCase())

export function isSimulatorAdmin(address: string | undefined): boolean {
  if (!address) return false
  return SIMULATOR_ADMIN_WALLETS.includes(address.toLowerCase())
}
