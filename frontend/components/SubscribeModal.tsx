import React from 'react';
import { X, Coins } from 'lucide-react';
import { Button } from 'components/ui/button';

interface SubscribeModalProps {
  show: boolean;
  onClose: () => void;
  subscriptionPlans: any[];
  onSubscribe: (planId: string) => void;
  isPending: boolean;
  t: any;
}

const SubscribeModal: React.FC<SubscribeModalProps> = ({ show, onClose, subscriptionPlans, onSubscribe, isPending, t }) => {
  if (!show) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto p-4 sm:p-8 relative transition-colors">
        <button 
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 touch-target tap-highlight transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
        <h2 className="text-xl sm:text-2xl font-bold text-center mb-6 sm:mb-8 text-gray-900 dark:text-gray-100 transition-colors">{t.subscription.title}</h2>
        <div className="flex justify-center gap-4 sm:gap-6 mb-6 sm:mb-8">
          <button className="px-4 sm:px-6 py-2 rounded-full bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm touch-target transition-colors">
            {t.subscription.plan}
          </button>
          <button className="px-4 sm:px-6 py-2 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm touch-target transition-colors">
            {t.subscription.addon}
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {subscriptionPlans.map((plan) => (
            <div key={plan.id} className={`border border-gray-200 dark:border-gray-700 rounded-xl p-4 sm:p-6 relative transition-colors ${plan.isPopular ? 'bg-gray-50 dark:bg-gray-800' : 'bg-white dark:bg-gray-900'}`}>
              {plan.isEarlyBird && (
                <div className="absolute -right-8 sm:-right-12 top-4 bg-red-100 dark:bg-red-900 text-red-500 dark:text-red-300 px-8 sm:px-12 py-1 rotate-45 text-xs transition-colors">
                  {t.subscription.earlyBird}
                </div>
              )}
              {plan.isPopular && (
                <div className="absolute -right-8 sm:-right-12 top-4 bg-blue-100 dark:bg-blue-900 text-blue-500 dark:text-blue-300 px-8 sm:px-12 py-1 rotate-45 text-xs transition-colors">
                  {t.subscription.bestValue}
                </div>
              )}
              <div className="text-lg sm:text-xl font-bold mb-2 text-gray-900 dark:text-gray-100 transition-colors">{plan.name}</div>
              <div className="text-gray-500 dark:text-gray-400 line-through mb-1 transition-colors">${plan.originalPrice}.00</div>
              <div className="text-2xl sm:text-3xl font-bold mb-4 text-gray-900 dark:text-gray-100 transition-colors">
                ${plan.price}.00<span className="text-sm text-gray-500 dark:text-gray-400">/month</span>
              </div>
              <Button 
                className={`w-full py-2 mb-4 sm:mb-6 touch-target transition-colors ${
                  plan.id === 'free' 
                    ? 'border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100' 
                    : plan.isPopular 
                      ? 'bg-[#1E90FF] hover:bg-[#187bcd] text-white' 
                      : 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-200'
                }`}
                onClick={() => onSubscribe(plan.id)}
                disabled={isPending}
              >
                {plan.id === 'free' ? t.subscription.currentPlan : t.subscription.subscribe}
              </Button>
              <div className="flex items-center gap-2 mb-4">
                <Coins className="w-4 h-4 text-gray-400 dark:text-gray-500 transition-colors" />
                <span className="font-semibold text-gray-900 dark:text-gray-100 transition-colors">{plan.coins}</span>
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-2 transition-colors">
                {plan.id === 'free' ? t.subscription.newUserGift : t.subscription.validForMonth}
              </div>
              {plan.features.length > 0 && (
                <ul className="space-y-2 sm:space-y-3 text-sm">
                  {plan.features.map((feature: string, index: number) => (
                    <li key={index} className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center">
                        <div className="w-2 h-2 bg-white rounded-full"></div>
                      </div>
                      <span className="text-gray-700 dark:text-gray-300 transition-colors">{feature}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SubscribeModal;
