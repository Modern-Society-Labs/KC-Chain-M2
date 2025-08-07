import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ApolloProvider } from '@apollo/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { WagmiProvider } from 'wagmi'
import App from './App.tsx'
import { apolloClient } from './lib/apollo'
import { queryClient, wagmiConfig } from './config/wallet'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <ApolloProvider client={apolloClient}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ApolloProvider>
      </QueryClientProvider>
    </WagmiProvider>
  </React.StrictMode>,
) 