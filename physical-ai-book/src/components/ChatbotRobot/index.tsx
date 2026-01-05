import React from 'react';
import { motion } from 'framer-motion';
import styles from './styles.module.css';

interface ChatbotRobotProps {
  isOpen?: boolean;
  onClick?: () => void;
}

export default function ChatbotRobot({ isOpen = false, onClick }: ChatbotRobotProps) {
  return (
    <motion.button
      className={styles.robotButton}
      onClick={onClick}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      animate={{
        rotate: isOpen ? 0 : [0, -10, 10, -10, 0],
      }}
      transition={{
        rotate: {
          duration: 2,
          repeat: Infinity,
          repeatDelay: 3,
        },
      }}
      aria-label={isOpen ? "Close chat" : "Open chat"}
    >
      <svg
        width="60"
        height="60"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={styles.robotSvg}
      >
        {/* Robot Head */}
        <motion.g
          animate={{
            y: isOpen ? 0 : [0, -2, 0],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          {/* Antenna */}
          <motion.line
            x1="50"
            y1="20"
            x2="50"
            y2="10"
            stroke="url(#antennaGradient)"
            strokeWidth="2"
            strokeLinecap="round"
            animate={{
              y1: [20, 18, 20],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
            }}
          />
          <motion.circle
            cx="50"
            cy="8"
            r="3"
            fill="#00d4ff"
            animate={{
              opacity: [0.5, 1, 0.5],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
            }}
          />

          {/* Head */}
          <rect
            x="30"
            y="20"
            width="40"
            height="35"
            rx="8"
            fill="url(#headGradient)"
            stroke="#2980b9"
            strokeWidth="2"
          />

          {/* Eyes */}
          <motion.g>
            <motion.circle
              cx="42"
              cy="35"
              r="5"
              fill="#00d4ff"
              animate={{
                opacity: [1, 0.3, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
              }}
            />
            <motion.circle
              cx="58"
              cy="35"
              r="5"
              fill="#00d4ff"
              animate={{
                opacity: [1, 0.3, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
              }}
            />
            {/* Eye highlights */}
            <circle cx="43" cy="33" r="2" fill="#ffffff" opacity="0.8" />
            <circle cx="59" cy="33" r="2" fill="#ffffff" opacity="0.8" />
          </motion.g>

          {/* Mouth/Speaker */}
          <motion.rect
            x="40"
            y="45"
            width="20"
            height="3"
            rx="1.5"
            fill="#2980b9"
            animate={{
              scaleX: isOpen ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 0.5,
              repeat: isOpen ? Infinity : 0,
            }}
          />
        </motion.g>

        {/* Body */}
        <motion.g
          animate={{
            y: isOpen ? 0 : [0, 1, 0],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.2,
          }}
        >
          <rect
            x="25"
            y="55"
            width="50"
            height="30"
            rx="5"
            fill="url(#bodyGradient)"
            stroke="#2980b9"
            strokeWidth="2"
          />

          {/* Chest panel */}
          <rect
            x="42"
            y="62"
            width="16"
            height="16"
            rx="2"
            fill="#1a1f3a"
            opacity="0.3"
          />

          {/* Status lights */}
          <motion.circle
            cx="45"
            cy="66"
            r="1.5"
            fill="#00ff88"
            animate={{
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
            }}
          />
          <motion.circle
            cx="50"
            cy="66"
            r="1.5"
            fill="#00d4ff"
            animate={{
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: 0.3,
            }}
          />
          <motion.circle
            cx="55"
            cy="66"
            r="1.5"
            fill="#ff6b6b"
            animate={{
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: 0.6,
            }}
          />
        </motion.g>

        {/* Arms */}
        <motion.g
          animate={{
            rotate: isOpen ? 0 : [0, 5, -5, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
          }}
          style={{ originX: '20px', originY: '65px' }}
        >
          <rect
            x="15"
            y="60"
            width="10"
            height="20"
            rx="3"
            fill="url(#armGradient)"
          />
          <circle cx="20" cy="82" r="4" fill="#2980b9" />
        </motion.g>

        <motion.g
          animate={{
            rotate: isOpen ? 0 : [0, -5, 5, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
          }}
          style={{ originX: '80px', originY: '65px' }}
        >
          <rect
            x="75"
            y="60"
            width="10"
            height="20"
            rx="3"
            fill="url(#armGradient)"
          />
          <circle cx="80" cy="82" r="4" fill="#2980b9" />
        </motion.g>

        {/* Gradients */}
        <defs>
          <linearGradient id="headGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#5dade2" />
            <stop offset="100%" stopColor="#3498db" />
          </linearGradient>
          <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3498db" />
            <stop offset="100%" stopColor="#2980b9" />
          </linearGradient>
          <linearGradient id="armGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3498db" />
            <stop offset="100%" stopColor="#2472a4" />
          </linearGradient>
          <linearGradient id="antennaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#00d4ff" />
            <stop offset="100%" stopColor="#3498db" />
          </linearGradient>
        </defs>

        {/* Glow effect */}
        <motion.circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="#3498db"
          strokeWidth="1"
          opacity="0.3"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.1, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
          }}
        />
      </svg>

      {/* New messages indicator */}
      {!isOpen && (
        <motion.div
          className={styles.notificationDot}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          exit={{ scale: 0 }}
        />
      )}
    </motion.button>
  );
}
