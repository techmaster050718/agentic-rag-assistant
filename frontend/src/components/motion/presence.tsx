"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ReactNode } from "react";

interface PresenceProps {
  show: boolean;
  children: ReactNode;
  duration?: number;
}

export function Presence({ show, children, duration = 0.2 }: PresenceProps) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
