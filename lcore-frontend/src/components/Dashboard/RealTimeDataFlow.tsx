import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Radio, 
  ArrowRight, 
  Cpu, 
  Shield,
  Zap,
  CheckCircle,
  Clock
} from 'lucide-react';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';
import { format } from 'date-fns';

// GraphQL query for recent inputs
const GET_RECENT_INPUTS = gql`
  query GetRecentInputs($first: Int!) {
    inputs(first: $first, orderBy: TIMESTAMP_DESC) {
      edges {
        node {
          index
          timestamp
          msgSender
          payload
        }
      }
    }
  }
`;

interface DataFlowStep {
  id: string;
  title: string;
  icon: React.ElementType;
  status: 'pending' | 'processing' | 'completed';
  description: string;
  color: string;
}

export const RealTimeDataFlow: React.FC = () => {
  const currentStep = 0; // Static - no animation to prevent glitches
  const [dataFlowSteps, setDataFlowSteps] = useState<DataFlowStep[]>([
    {
      id: 'input',
      title: 'Device Data Input',
      icon: Radio,
      status: 'pending',
      description: '',
      color: 'text-accent-cyan'
    },
    {
      id: 'processing',
      title: 'Cartesi Processing',
      icon: Cpu,
      status: 'pending',
      description: '',
      color: 'text-locale-blue'
    },
    {
      id: 'encryption',
      title: 'Dual Encryption',
      icon: Shield,
      status: 'pending',
      description: '',
      color: 'text-accent-purple'
    },
    {
      id: 'output',
      title: 'Community Access',
      icon: CheckCircle,
      status: 'pending',
      description: '',
      color: 'text-accent-green'
    }
  ]);

  // Fetch recent inputs from GraphQL (no polling to prevent glitches)
  const { data: inputsData, loading } = useQuery(GET_RECENT_INPUTS, {
    variables: { first: 5 }
  });

  // Static data flow - no animation to prevent glitches
  useEffect(() => {
    // Set all steps to completed for a clean static display
    setDataFlowSteps(steps => 
      steps.map((step) => ({
        ...step,
        status: 'completed'
      }))
    );
  }, []);

  const recentInputs = inputsData?.inputs?.edges || [];

  return (
    <div className="locale-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-locale-gradient rounded-lg flex items-center justify-center">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-h2">Real-Time Data Flow</h3>
        <div className="flex items-center gap-2 ml-auto">
          <div className="w-2 h-2 bg-accent-green rounded-full animate-pulse"></div>
          <span className="text-sm text-locale-gray font-medium">Live Processing</span>
        </div>
      </div>

      {/* Data Flow Visualization */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
        {dataFlowSteps.map((step, index) => {
          const IconComponent = step.icon;
          const isActive = index === currentStep;
          const isCompleted = step.status === 'completed';
          
          return (
            <motion.div
              key={step.id}
              className={`relative p-3 sm:p-4 rounded-lg border-2 transition-all duration-300 ${
                isActive 
                  ? 'border-accent-green bg-accent-green/5' 
                  : isCompleted 
                    ? 'border-accent-cyan bg-accent-cyan/5'
                    : 'border-locale-gray-light bg-white'
              }`}
              animate={isActive ? { scale: 1.02 } : { scale: 1 }}
            >
              <div className="flex items-center gap-2 sm:gap-3 mb-2">
                <IconComponent 
                  className={`w-4 h-4 sm:w-5 sm:h-5 ${step.color} ${isActive ? 'animate-pulse' : ''}`} 
                />
                <span className="font-medium text-locale-gray-dark text-sm sm:text-base">{step.title}</span>
              </div>
              
              <p className="text-xs sm:text-sm text-locale-gray">{step.description}</p>
              
              {/* Progress indicator */}
              {isActive && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-accent-lime animate-pulse rounded-b-locale"></div>
              )}
              
              {/* Arrow to next step */}
              {index < dataFlowSteps.length - 1 && (
                <ArrowRight className="absolute -right-3 top-1/2 transform -translate-y-1/2 w-6 h-6 text-urban-grey bg-cloud-white rounded-full p-1 hidden md:block" />
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Recent Inputs */}
      <div>
        <h4 className="font-medium text-urban-grey mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Recent Data Inputs ({recentInputs.length})
        </h4>
        
        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="loading-skeleton h-16 rounded-locale"></div>
            ))}
          </div>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {recentInputs.map((input: any, index: number) => {
              const inputData = input.node;
              let payloadPreview = 'Encrypted data';
              
              try {
                // Try to decode hex payload
                const hexPayload = inputData.payload;
                if (hexPayload.startsWith('0x')) {
                  const decoded = Buffer.from(hexPayload.slice(2), 'hex').toString('utf8');
                  const parsed = JSON.parse(decoded);
                  payloadPreview = `${parsed.sensor_type || 'sensor'}: ${parsed.reading || 'N/A'}${parsed.unit || ''}`;
                }
              } catch (e) {
                // Keep default encrypted preview
              }
              
              return (
                <motion.div
                  key={inputData.index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-4 p-3 bg-cloud-white/50 rounded-locale border border-grid-lines"
                >
                  <div className="w-2 h-2 bg-accent-lime rounded-full"></div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="font-mono text-locale-blue">#{inputData.index}</span>
                      <span className="text-urban-grey">{payloadPreview}</span>
                    </div>
                    <div className="text-xs text-urban-grey/60 mt-1">
                      {format(new Date(inputData.timestamp * 1000), 'HH:mm:ss')} • 
                      {inputData.msgSender.slice(0, 8)}...
                    </div>
                  </div>
                  <div className="privacy-indicator">
                    <Shield className="w-3 h-3" />
                    <span>Encrypted</span>
                  </div>
                </motion.div>
              );
            })}
            
            {recentInputs.length === 0 && (
              <div className="text-center py-8 text-urban-grey/60">
                <Radio className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Waiting for IoT data inputs...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}; 