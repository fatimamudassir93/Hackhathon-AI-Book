import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import RoboticArm from '@site/src/components/RoboticArm';
import Heading from '@theme/Heading';
import { motion } from 'framer-motion';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className={styles.heroBackground}>
        {/* Animated grid background */}
        <div className={styles.gridBackground}></div>

        {/* Floating circuit patterns */}
        <div className={styles.circuitPattern}></div>
      </div>

      <div className="container">
        <div className={styles.heroContent}>
          <motion.div
            className={styles.heroText}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <Heading as="h1" className={styles.heroTitle}>
                {siteConfig.title}
              </Heading>
            </motion.div>

            <motion.p
              className={styles.heroSubtitle}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              {siteConfig.tagline}
            </motion.p>

            <motion.div
              className={styles.buttons}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
            >
              <Link
                className={clsx('button button--lg', styles.primaryButton)}
                to="/docs/intro">
                Start Learning
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" style={{ marginLeft: '8px' }}>
                  <path d="M10 3L8.59 4.41L13.17 9H3v2h10.17l-4.58 4.59L10 17l7-7-7-7z"/>
                </svg>
              </Link>
              <Link
                className={clsx('button button--lg', styles.secondaryButton)}
                to="/docs/intro">
                Explore Chapters
              </Link>
            </motion.div>

            {/* Tech stats */}
            <motion.div
              className={styles.techStats}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.6 }}
            >
              <div className={styles.statItem}>
                <div className={styles.statValue}>10+</div>
                <div className={styles.statLabel}>Chapters</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statValue}>100+</div>
                <div className={styles.statLabel}>Topics</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statValue}>AI</div>
                <div className={styles.statLabel}>Powered</div>
              </div>
            </motion.div>
          </motion.div>

          <motion.div
            className={styles.heroVisual}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <RoboticArm />
          </motion.div>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="A comprehensive guide to Physical AI and humanoid robotics">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
