insert into public.organizations (id, name, slug)
values
  ('00000000-0000-4000-8000-000000000001', 'Northstar Manufacturing', 'northstar')
on conflict (id) do nothing;

insert into public.plants (id, organization_id, name, location)
values
  ('00000000-0000-4000-8000-000000000101', '00000000-0000-4000-8000-000000000001', 'Pune Plant A', 'Pune, India')
on conflict (id) do nothing;

insert into public.profiles (id, user_id, organization_id, plant_id, assigned_plant_ids, role, display_name, email)
values
  ('00000000-0000-4000-8000-000000000201', '00000000-0000-4000-8000-000000000901', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000101', array['00000000-0000-4000-8000-000000000101']::uuid[], 'supervisor', 'Asha Supervisor', 'asha.supervisor@example.com'),
  ('00000000-0000-4000-8000-000000000202', '00000000-0000-4000-8000-000000000902', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000101', array['00000000-0000-4000-8000-000000000101']::uuid[], 'technician', 'Ravi Technician', 'ravi.technician@example.com')
on conflict (id) do nothing;

insert into public.assets (id, organization_id, plant_id, created_by, asset_tag, name, line_name, status, risk_score, metadata)
values
  (
    '00000000-0000-4000-8000-000000000301',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000201',
    'L2-SPINDLE-01',
    'Line 2 Spindle',
    'Line 2',
    'high_risk',
    0.8700,
    '{"torque_nm": 82.4, "tool_wear_min": 238, "operator_note": "vibration reported during last batch"}'::jsonb
  ),
  (
    '00000000-0000-4000-8000-000000000302',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000201',
    'L1-PUMP-03',
    'Coolant Pump 3',
    'Line 1',
    'watch',
    0.4100,
    '{"flow_lpm": 41.2, "pressure_bar": 2.7}'::jsonb
  )
on conflict (id) do nothing;

insert into public.incidents (id, organization_id, plant_id, asset_id, created_by, title, description, severity, status, observed_at)
values
  (
    '00000000-0000-4000-8000-000000000401',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000301',
    '00000000-0000-4000-8000-000000000202',
    'High spindle torque and vibration',
    'Operator reported vibration; telemetry shows torque spike and rising tool wear.',
    'high',
    'open',
    now() - interval '2 hours'
  )
on conflict (id) do nothing;

insert into public.documents (id, organization_id, plant_id, created_by, title, document_type, source_uri, checksum)
values
  (
    '00000000-0000-4000-8000-000000000501',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000201',
    'SOP-17 Spindle Vibration Response',
    'sop',
    'seed://sop-17-spindle-vibration',
    'seed-sop-17'
  ),
  (
    '00000000-0000-4000-8000-000000000502',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000201',
    'Manual-08 CNC Spindle Maintenance',
    'manual',
    'seed://manual-08-cnc-spindle',
    'seed-manual-08'
  )
on conflict (id) do nothing;

insert into public.document_chunks (
  id,
  organization_id,
  plant_id,
  document_id,
  created_by,
  chunk_index,
  content,
  citation_label,
  page_number,
  title,
  source_uri,
  source_page,
  metadata
)
values
  (
    '00000000-0000-4000-8000-000000000601',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000501',
    '00000000-0000-4000-8000-000000000201',
    0,
    'If spindle vibration is reported with elevated torque, reduce feed rate, pause noncritical production, and inspect tool wear before the next shift begins.',
    'SOP-17#chunk-0',
    2,
    'SOP-17 Spindle Vibration Response',
    'seed://sop-17-spindle-vibration',
    2,
    '{"section": "Initial response"}'::jsonb
  ),
  (
    '00000000-0000-4000-8000-000000000602',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000501',
    '00000000-0000-4000-8000-000000000201',
    1,
    'Before spindle inspection, follow lockout-tagout, verify zero energy state, and record bearing temperature and vibration readings in the maintenance log.',
    'SOP-17#chunk-1',
    3,
    'SOP-17 Spindle Vibration Response',
    'seed://sop-17-spindle-vibration',
    3,
    '{"section": "Safety controls"}'::jsonb
  ),
  (
    '00000000-0000-4000-8000-000000000603',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000502',
    '00000000-0000-4000-8000-000000000201',
    0,
    'Rising tool wear combined with abnormal torque can indicate bearing preload issues, tool imbalance, or early spindle degradation. Schedule inspection within one shift if risk is high.',
    'Manual-08#chunk-0',
    14,
    'Manual-08 CNC Spindle Maintenance',
    'seed://manual-08-cnc-spindle',
    14,
    '{"section": "Failure modes"}'::jsonb
  )
on conflict (id) do nothing;

insert into public.model_predictions (id, organization_id, plant_id, asset_id, created_by, model_name, model_version, risk_score, predicted_label, features, explanation)
values
  (
    '00000000-0000-4000-8000-000000000701',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000301',
    '00000000-0000-4000-8000-000000000201',
    'ai4i-failure-risk',
    'seed-v0',
    0.8700,
    'high_failure_risk',
    '{"torque_nm": 82.4, "tool_wear_min": 238, "vibration_reported": true}'::jsonb,
    '{"top_factors": ["tool_wear_min", "torque_nm", "vibration_reported"]}'::jsonb
  )
on conflict (id) do nothing;

insert into public.rag_queries (id, organization_id, plant_id, created_by, query, answer, citations, model_used, fallback_used, latency_ms)
values
  (
    '00000000-0000-4000-8000-000000000801',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000201',
    'Line 2 spindle torque is high, tool wear is rising, and the operator reported vibration. What should the next shift do?',
    'Reduce feed rate, perform lockout-tagout, inspect tool wear and spindle vibration, and draft an urgent next-shift work order.',
    '[{"chunk_id": "00000000-0000-4000-8000-000000000601", "label": "SOP-17#chunk-0"}, {"chunk_id": "00000000-0000-4000-8000-000000000602", "label": "SOP-17#chunk-1"}, {"chunk_id": "00000000-0000-4000-8000-000000000603", "label": "Manual-08#chunk-0"}]'::jsonb,
    'seed-local',
    true,
    142
  )
on conflict (id) do nothing;

insert into public.work_orders (id, organization_id, plant_id, asset_id, incident_id, created_by, title, description, priority, status, ai_recommendation, due_at)
values
  (
    '00000000-0000-4000-8000-000000000901',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000301',
    '00000000-0000-4000-8000-000000000401',
    '00000000-0000-4000-8000-000000000201',
    'Inspect Line 2 spindle vibration and tool wear',
    'Next shift should reduce load, lock out the spindle, inspect tool wear and bearing vibration, then record readings before restart.',
    'urgent',
    'draft',
    '{"urgency": "urgent", "recommended_actions": ["Reduce feed rate", "Run lockout-tagout", "Inspect tool wear", "Record vibration and bearing temperature"], "citations": ["SOP-17#chunk-0", "SOP-17#chunk-1", "Manual-08#chunk-0"]}'::jsonb,
    now() + interval '8 hours'
  )
on conflict (id) do nothing;

insert into public.audit_logs (id, organization_id, plant_id, created_by, actor_user_id, action, entity_type, entity_id, details)
values
  (
    '00000000-0000-4000-8000-000000000a01',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000201',
    '00000000-0000-4000-8000-000000000901',
    'seed.demo_created',
    'work_order',
    '00000000-0000-4000-8000-000000000901',
    '{"source": "supabase/seed.sql"}'::jsonb
  )
on conflict (id) do nothing;
