import { useReducedMotion } from 'framer-motion';
import type { MotionProps } from 'framer-motion';

/**
 * Wraps a set of framer-motion props so they collapse to nothing when the visitor has asked
 * their system for reduced motion.
 *
 * The site animated 39 elements on scroll and none of them consulted the preference, which
 * is the WCAG 2.3.3 failure and, for anyone with a vestibular disorder, the difference
 * between a readable page and an unusable one. Returning the props unchanged or empty — as
 * opposed to setting `transition: { duration: 0 }` — also means the element is never handed
 * an opacity-0 initial state it might fail to animate away from.
 *
 * Examples:
 *   >>> // with the preference set, the element renders at its final state immediately
 *   >>> motionSafe({ initial: { opacity: 0 }, whileInView: { opacity: 1 } })
 *   {}
 */
export function useMotionSafe(): (props: MotionProps) => MotionProps {
    const prefersReducedMotion = useReducedMotion();
    return (props: MotionProps) => (prefersReducedMotion ? {} : props);
}
