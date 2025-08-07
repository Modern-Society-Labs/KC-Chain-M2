// AppKit Wallet Configuration for L{CORE}
import { createAppKit } from '@reown/appkit/react'
import { WagmiAdapter } from '@reown/appkit-adapter-wagmi'
import { localeNetwork } from './networks'
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
  }
})

export const queryClient = new QueryClient()
export const wagmiConfig = wagmiAdapter.wagmiConfig

// Whitelist for IoT simulator control
export const SIMULATOR_ADMIN_WALLETS = [
  '0x6D9823a18502AC88B0BC6b8FDDC19c28A69E05BD', // Replace with actual admin wallet addresses
  '0x304Fb7fcc3a41fCe12e33d0E1d63B6b6De79FA8D', // Add more admin wallets as needed
  // Add your admin wallet addresses here
].map(addr => addr.toLowerCase())

export function isSimulatorAdmin(address: string | undefined): boolean {
  if (!address) return false
  return SIMULATOR_ADMIN_WALLETS.includes(address.toLowerCase())
}
