import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AgentsView from '@/modules/registry/views/AgentsView.vue'
import DatasetsView from '@/modules/evaluate/views/DatasetsView.vue'
import EvalRunsView from '@/modules/evaluate/views/EvalRunsView.vue'
import PlaygroundView from '@/modules/evaluate/views/PlaygroundView.vue'
import AnalyticsView from '@/modules/analytics/views/AnalyticsView.vue'
import SettingsView from '@/modules/settings/views/SettingsView.vue'

const cases = [
  { name: 'AgentsView',     Component: AgentsView,     title: 'Agents' },
  { name: 'DatasetsView',   Component: DatasetsView,   title: 'Datasets' },
  { name: 'EvalRunsView',   Component: EvalRunsView,   title: 'Eval Runs' },
  { name: 'PlaygroundView', Component: PlaygroundView, title: 'Playground' },
  { name: 'AnalyticsView',  Component: AnalyticsView,  title: 'Analytics' },
  { name: 'SettingsView',   Component: SettingsView,   title: 'Settings' },
]

describe('Shell views', () => {
  it.each(cases)('$name renders page title "$title" and shell-empty', ({ Component, title }) => {
    const wrapper = mount(Component)
    expect(wrapper.find('.page-title').text()).toBe(title)
    expect(wrapper.find('.shell-empty').exists()).toBe(true)
  })
})
