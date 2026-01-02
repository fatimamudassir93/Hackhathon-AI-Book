import React from 'react';
import { motion } from 'framer-motion';
import styles from './styles.module.css';

export default function RoboticArm() {
  return (
    <div className={styles.roboticArmContainer}>
      <svg
        width="400"
        height="500"
        viewBox="0 0 400 500"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={styles.roboticArmSvg}
      >
        {/* Base */}
        <motion.g
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <rect
            x="150"
            y="440"
            width="100"
            height="40"
            fill="url(#baseGradient)"
            rx="5"
          />
          <circle cx="200" cy="460" r="8" fill="#FFD700" />
        </motion.g>

        {/* Lower Arm (Joint 1) */}
        <motion.g
          animate={{
            rotate: [0, 10, -10, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ originX: '200px', originY: '440px' }}
        >
          <rect
            x="190"
            y="340"
            width="20"
            height="100"
            fill="url(#armGradient)"
            rx="3"
          />
          <circle cx="200" cy="440" r="15" fill="#1E90FF" stroke="#0066CC" strokeWidth="2" />
          <circle cx="200" cy="340" r="12" fill="#1E90FF" stroke="#0066CC" strokeWidth="2" />
        </motion.g>

        {/* Middle Arm (Joint 2) */}
        <motion.g
          animate={{
            rotate: [0, -15, 15, 0],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.5,
          }}
          style={{ originX: '200px', originY: '340px' }}
        >
          <rect
            x="190"
            y="240"
            width="20"
            height="100"
            fill="url(#armGradient)"
            rx="3"
          />
          <circle cx="200" cy="340" r="12" fill="#1E90FF" stroke="#0066CC" strokeWidth="2" />
          <circle cx="200" cy="240" r="12" fill="#1E90FF" stroke="#0066CC" strokeWidth="2" />
        </motion.g>

        {/* Upper Arm (Joint 3) */}
        <motion.g
          animate={{
            rotate: [0, 8, -8, 0],
          }}
          transition={{
            duration: 3.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
          style={{ originX: '200px', originY: '240px' }}
        >
          <rect
            x="190"
            y="160"
            width="20"
            height="80"
            fill="url(#armGradient)"
            rx="3"
          />
          <circle cx="200" cy="240" r="12" fill="#1E90FF" stroke="#0066CC" strokeWidth="2" />
        </motion.g>

        {/* Gripper/End Effector */}
        <motion.g
          animate={{
            rotate: [0, 20, -20, 0],
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1.5,
          }}
          style={{ originX: '200px', originY: '160px' }}
        >
          {/* Gripper base */}
          <rect
            x="185"
            y="140"
            width="30"
            height="20"
            fill="url(#gripperGradient)"
            rx="3"
          />

          {/* Left gripper finger */}
          <motion.rect
            x="175"
            y="120"
            width="10"
            height="25"
            fill="#FF6B6B"
            rx="2"
            animate={{
              x: [175, 170, 175],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          {/* Right gripper finger */}
          <motion.rect
            x="215"
            y="120"
            width="10"
            height="25"
            fill="#FF6B6B"
            rx="2"
            animate={{
              x: [215, 220, 215],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          {/* Gripper center */}
          <circle cx="200" cy="160" r="10" fill="#FF6B6B" stroke="#CC5555" strokeWidth="2" />
        </motion.g>

        {/* Sensor/Camera on gripper */}
        <motion.circle
          cx="200"
          cy="130"
          r="6"
          fill="#00FF00"
          animate={{
            opacity: [0.3, 1, 0.3],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Connection wires */}
        <motion.path
          d="M 195 440 Q 180 400, 195 340"
          stroke="#666"
          strokeWidth="2"
          strokeDasharray="5,5"
          fill="none"
          animate={{
            strokeDashoffset: [0, -10],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "linear",
          }}
        />
        <motion.path
          d="M 205 340 Q 220 300, 205 240"
          stroke="#666"
          strokeWidth="2"
          strokeDasharray="5,5"
          fill="none"
          animate={{
            strokeDashoffset: [0, -10],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "linear",
          }}
        />

        {/* Gradients */}
        <defs>
          <linearGradient id="baseGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2C3E50" />
            <stop offset="100%" stopColor="#1A252F" />
          </linearGradient>
          <linearGradient id="armGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3498DB" />
            <stop offset="50%" stopColor="#2980B9" />
            <stop offset="100%" stopColor="#1E6FA8" />
          </linearGradient>
          <linearGradient id="gripperGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#E74C3C" />
            <stop offset="100%" stopColor="#C0392B" />
          </linearGradient>
        </defs>
      </svg>

      {/* Floating particles for robotic atmosphere */}
      <div className={styles.particles}>
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className={styles.particle}
            animate={{
              y: [0, -100, 0],
              x: [0, Math.random() * 40 - 20, 0],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut",
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
