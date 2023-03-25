import bpy
import bmesh

from . import utilities_uv
from . import op_uv_crop



class op(bpy.types.Operator):
	bl_idname = "uv.textools_uv_fill"
	bl_label = "Fill"
	bl_description = "Fill UV selection to UV canvas"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if bpy.context.area.ui_type != 'UV':
			return False
		if not bpy.context.active_object:
			return False
		if bpy.context.active_object.type != 'MESH':
			return False
		if bpy.context.active_object.mode != 'EDIT':
			return False
		if not bpy.context.object.data.uv_layers:
			return False
		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False
		return True
	

	def execute(self, context):
		selected_obs = [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']
		# Clean selection so that only entirely selected UV faces remain selected
		bpy.ops.uv.select_split()

		selection = None
		if len(selected_obs) <= 1:
			bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
			uv_layers = bm.loops.layers.uv.verify()
			selection = utilities_uv.get_selected_uv_faces(bm, uv_layers)
			if not selection:
				return {'CANCELLED'}
			utilities_uv.alignMinimalBounds(bm, uv_layers, selection)

		elif len(selected_obs) > 1:
			# Rotate UV selection of all selected objects to the shared minimal bounds
			utilities_uv.alignMinimalBounds_multi()

		# Expand UV selection of all selected objects towards the UV space 0-1 limits
		op_uv_crop.crop(self, context, distort=True, selection=selection)

		return {'FINISHED'}


bpy.utils.register_class(op)
