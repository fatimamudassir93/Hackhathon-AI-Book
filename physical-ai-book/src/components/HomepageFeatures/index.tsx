import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import { motion } from 'framer-motion';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  icon: string;
  description: ReactNode;
  color: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Comprehensive Learning',
    icon: '🤖',
    color: '#3498db',
    description: (
      <>
        Deep dive into Physical AI and humanoid robotics with structured chapters
        covering fundamentals to advanced topics in AI-powered robotic systems.
      </>
    ),
  },
  {
    title: 'Interactive Content',
    icon: '⚡',
    color: '#00d4ff',
    description: (
      <>
        Engage with AI-powered chatbot assistance, real-time code examples, and
        interactive visualizations to enhance your learning experience.
      </>
    ),
  },
  {
    title: 'Cutting-Edge Topics',
    icon: '🔬',
    color: '#e74c3c',
    description: (
      <>
        Explore the latest in humanoid robotics, motion control, sensor fusion,
        and AI integration for physical autonomous systems.
      </>
    ),
  },
  {
    title: 'Practical Applications',
    icon: '🛠️',
    color: '#f39c12',
    description: (
      <>
        Learn through real-world applications and implementations that bridge
        theory with practical robotic system development.
      </>
    ),
  },
  {
    title: 'Research-Backed',
    icon: '📚',
    color: '#9b59b6',
    description: (
      <>
        Content based on the latest research and industry best practices in
        Physical AI and autonomous robotic systems.
      </>
    ),
  },
  {
    title: 'Community Driven',
    icon: '🌐',
    color: '#16a085',
    description: (
      <>
        Join a growing community of robotics enthusiasts, researchers, and
        developers shaping the future of Physical AI.
      </>
    ),
  },
];

function Feature({title, icon, description, color}: FeatureItem & {index: number}) {
  return (
    <motion.div
      className={clsx('col col--4')}
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -8 }}
    >
      <div className={styles.featureCard}>
        <motion.div
          className={styles.iconWrapper}
          style={{ backgroundColor: `${color}15` }}
          whileHover={{ scale: 1.1, rotate: 5 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          <span className={styles.icon} style={{ color: color }}>
            {icon}
          </span>
          <motion.div
            className={styles.iconGlow}
            style={{ backgroundColor: color }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </motion.div>
        <Heading as="h3" className={styles.featureTitle}>
          {title}
        </Heading>
        <p className={styles.featureDescription}>{description}</p>
      </div>
    </motion.div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <motion.div
          className={styles.sectionHeader}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <Heading as="h2" className={styles.sectionTitle}>
            Why Learn Physical AI & Robotics?
          </Heading>
          <p className={styles.sectionSubtitle}>
            Master the intersection of artificial intelligence and physical robotics
          </p>
        </motion.div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} index={idx} />
          ))}
        </div>
      </div>
    </section>
  );
}
