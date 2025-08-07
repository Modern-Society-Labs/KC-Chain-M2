// Network Configuration for L{CORE}
import { defineChain } from 'viem'

export const localeNetwork = defineChain({
  id: 1205614515668104,
  name: 'Locale Network',
  nativeCurrency: {
    decimals: 18,
    name: 'ETH',
    symbol: 'ETH',
  },
  rpcUrls: {
    default: {
      http: ['https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200'],
      webSocket: ['wss://ws.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200'],
    },
  },
  blockExplorers: {
    default: { 
      name: 'Locale Network Explorer', 
      url: 'https://explorer-1205614515668104.devnet.alchemy.com' 
    },
  },
  contracts: {
    // Add contracts if needed
  },
  testnet: true,
})
