import React from 'react';
import { Shield, CheckCircle, Clock, ExternalLink } from 'lucide-react';

export const BlockchainVerification: React.FC = () => {
  return (
    <div className="locale-card">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-locale-blue" />
        <h3 className="text-h2">Blockchain Verification</h3>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-3 p-3 bg-accent-lime/10 rounded-locale">
          <CheckCircle className="w-5 h-5 text-accent-lime" />
          <div className="flex-1">
            <div className="font-medium text-urban-grey">Fraud-Proof Active</div>
            <div className="text-xs text-urban-grey/60">Cartesi verification enabled</div>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 bg-smart-city-teal/10 rounded-locale">
          <Shield className="w-5 h-5 text-smart-city-teal" />
          <div className="flex-1">
            <div className="font-medium text-urban-grey">ZK Proofs</div>
            <div className="text-xs text-urban-grey/60">Privacy preserved</div>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 bg-locale-blue/10 rounded-locale">
          <Clock className="w-5 h-5 text-locale-blue" />
          <div className="flex-1">
            <div className="font-medium text-urban-grey">Last Proof</div>
            <div className="text-xs text-urban-grey/60">2 minutes ago</div>
          </div>
        </div>
      </div>

      <button className="btn-secondary w-full mt-4 flex items-center justify-center gap-2">
        <ExternalLink className="w-4 h-4" />
        View on Locale Network
      </button>
    </div>
  );
}; 