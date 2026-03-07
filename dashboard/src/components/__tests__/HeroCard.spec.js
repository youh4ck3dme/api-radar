import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import HeroCard from '../HeroCard.vue'

describe('HeroCard.vue', () => {
    it('renders correctly', () => {
        const wrapper = mount(HeroCard)
        expect(wrapper.exists()).toBe(true)
    })

    it('contains the correct main text elements', () => {
        const wrapper = mount(HeroCard)
        // Check main title
        expect(wrapper.text()).toContain('API Centrum')
        // Check main description
        expect(wrapper.text()).toContain('Inteligentná správa domén a SSL certifikátov na jednom mieste')
        // Check button text
        expect(wrapper.text()).toContain('Začať správu')
    })

    it('has the correct base styling classes applied', () => {
        const wrapper = mount(HeroCard)
        // The main container should have specific tailwind classes 
        // based on our HeroCard implementation
        expect(wrapper.classes()).toContain('relative')
        expect(wrapper.classes()).toContain('w-full')
        expect(wrapper.classes()).toContain('rounded-3xl')

        // Check for inner components
        const accents = wrapper.find('.accents')
        expect(accents.exists()).toBe(true)

        const heroCardInner = wrapper.find('.hero-card')
        expect(heroCardInner.exists()).toBe(true)
    })
})
