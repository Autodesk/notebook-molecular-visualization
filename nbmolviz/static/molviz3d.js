var DONOTSEND = ['GLViewer','GLModel'];

define(["nbextensions/widgets/widgets/js/widget",
        "nbextensions/molviz/3Dmol"], function wireWidget(widget, manager){

        function processCubeFile(cubeData,uuid) {
            volumeData = new $3Dmol.VolumeData(cubeData, "cube");
            this.pyObjects[uuid] = volumeData;
        }

        function batchCommands(commands){
            var results = [];
            var viewer = this;
            commands.forEach(function (cmd){
                var fn = viewer[cmd[0]];
                var args = cmd[1];
                fn.apply(viewer, args);
                //results.push( fn.apply(viewer, args));
            });
            return results; // results are disabled because they sometimes lead to recursive JSON.
        }

        function renderPyShape(shape,spec,uuid,clickable){
            if(clickable == true){
                spec.clickable = true;
                spec.callback=this.widget.setSelectionTrait;
            }
            shape = this['add'+shape](spec);
            shape.pyid = uuid;
            this.pyObjects[uuid] = shape;
        }

        function removePyShape(shapeId){
            shape = this.pyObjects[shapeId];
            this.removeShape(shape);
        }

        function drawBond(atom1, atom2, order, spec) {
            spec.start = {}
                .x = atom1.x
                .y = atom1.y
                .z = atom1.z;
            spec.end = {}
                .x = atom1.x
                .y = atom1.y
                .z = atom1.z;

        }

        function setAtomColor(atom_json, color){
            var atoms = this.selectedAtoms(atom_json);
            atoms.forEach(function (atom){
                var style = atom.style;
                for (var s in style) {
                    if (atom.style.hasOwnProperty(s)) {
                        atom.style[s].color = color;
                    }
                }
            });
            this.forceRedraw();
        }

        function unsetAtomColor(atomJSON){
            var atoms = this.selectedAtoms(atomJSON);
            atoms.forEach(function(atom){
                for (var s in atom.style) {
                    if (atom.style.hasOwnProperty(s)) {
                        atom.style[s].color = undefined;
                    }

                }
            });
            this.forceRedraw()
        }

        function setColorArray(mapping){
            var atoms = this.selectedAtoms();
            for (var color in mapping){
                if (! mapping.hasOwnProperty(color)) continue;

                mapping[color].index.forEach(function (ind){ // this is probably fragile
                    var atom = atoms[ind];
                    if (atom.index != ind){
                        throw "selectedAtoms()["+ind+"].index != "+ind;
                    }
                    var style = atom.style;
                    for (var s in style) {
                        if (style.hasOwnProperty(s)) {
                            style[s].color = color;
                        }
                    }
                });
            }
            this.forceRedraw();
        }

        function renderPyLabel(text,spec,uuid){
            label = this.addLabel(text, spec);
            this.pyObjects[uuid] = label;
        }

        function removePyLabel(labelId){
            label = this.pyObjects[labelId];
            this.removeLabel(label);
        }

	    
        function drawIsosurface(dataId, shapeId, spec){
            data = this.pyObjects[dataId];
            shape = this.addIsosurface(data,spec);
            this.pyObjects[shapeId] = shape;
        }

        function addFrameFromList(positionList) {
            var oldatoms = this.selectedAtoms({});
            var newatoms = [];
            for (var i = 0; i < oldatoms.length; i++) {
                var atom = jQuery.extend({}, oldatoms[i]);
                atom.x = positionList[i][0];
                atom.y = positionList[i][1];
                atom.z = positionList[i][2];
                newatoms.push(atom);
            }
            var model = this.getModel(0);
            return model.addFrame(newatoms);
        }

        function setPositions(positionList) {
            var atoms = this.selectedAtoms();
            for (var i = 0; i < atoms.length; i++) {
                var atom = atoms[i];
                atom.x = positionList[i][0];
                atom.y = positionList[i][1];
                atom.z = positionList[i][2];
            }
            this.forceRedraw();
        }

        function forceRedraw(){
            // relies on adding the forceRedraw method
            this.getModel().forceRedraw();
        }

        function makeAtomsClickable(){
            this.setClickable({},true,this.widget.setSelectionTrait)
        }

        function setBonds(bonds){
            var atoms = this.selectedAtoms();
            bonds.forEach(function(bond){
                var a = atoms[bond.index];
                a.bonds = bond.nbr;
                a.bondOrder = bond.order;
            })
        }

        var MolViz3DBase = widget.DOMWidgetView.extend({

            render: function render() {
                document.last_3d_widget = this;
                this._where = this.model.get('_where');
                this.messages = [];
                this.viewerId = this.model.get('viewerId');
                if (this._where == 'inline') {
                    this.mydiv = document.createElement('div');
                    this.mydiv.style.width = this.model.get('_width');
                    this.mydiv.style.height = this.model.get('_height'); //not sure why this is necessary
                    this.mydiv.style.position = 'relative';
                    this.$el[0].appendChild(this.mydiv);
                } else if (this._where == 'right') {
                    this.pane = this.getRightPane();
                    this.divId = '#molviz_viewer_pane'
                } else {
                    throw "ERROR: did not recognize this._where="+this._where}


                //function is here to grab the correct "this" from closure
                //"this" is not this but actually refers to the atom JSON
                //I HATE YOU JAVASCRIPT
                var mywidget = this;
                function setSelectionTrait(){
                    result = {model:this.model,
                        index:this.index,
                        serial:this.serial,
                        pyid:this.pyid};
                    mywidget.model.set('_click_selection',result);
                    mywidget.model.save();
                }
                this.setSelectionTrait = setSelectionTrait;
                this.viewer = this.renderViewer();
                this.listenTo(this.model,'msg:custom',
                    this.handleMessage,this);

                this.send({'event':'ready'});
                console.log(this.viewerId+' is ready');
            },

            renderViewer: function renderViewer() {
                var glviewer = $3Dmol.createViewer( $(this.mydiv), {
                    defaultcolors: $3Dmol.rasmolElementColors});
                if(typeof($3Dmol.widgets)=='undefined'){$3Dmol.widgets = {};}
                $3Dmol.viewers[this.viewerId] = glviewer;
                $3Dmol.widgets[this.viewerId] = this;
                $3Dmol.last_viewer = glviewer;
                $3Dmol.last_widget = this;

                //Maybe want to remove this monkeypatching some day ...
		glviewer.setColorArray = setColorArray;
                glviewer.processCubeFile = processCubeFile;
                glviewer.pyObjects = {};
                glviewer.addFrameFromList = addFrameFromList;
                glviewer.drawIsosurface = drawIsosurface;
                glviewer.widget = this;
                glviewer.makeAtomsClickable = makeAtomsClickable;
                glviewer.renderPyShape = renderPyShape;
                glviewer.renderPyLabel = renderPyLabel;
                glviewer.removePyShape = removePyShape;
                glviewer.removePyLabel = removePyLabel;
                glviewer.setAtomColor = setAtomColor;
                glviewer.setPositions = setPositions;
                glviewer.forceRedraw = forceRedraw;
                glviewer.unsetAtomColor = unsetAtomColor;
                glviewer.batchCommands = batchCommands;
                glviewer.setBonds = setBonds;
                document.last_3dmol_viewer = glviewer;
                return glviewer;
            },



            getRightPane: function getRightPane(){
                var pane = $('#molviz_viewer_pane');
                if(pane.length != 0){
                    paneStyle = {right:0, top:0,
                        position:'absolute',
                        height:'100%',width:'40%'};
                    pane = document.createElement('div');
                    pane.id = 'molviz_viewer_pane';
                    $.extend(pane.style,paneStyle);
                    $('#site')[0].appendChild(pane);
                    this.makeNotebookFit(pane);
                }
                return pane
            },

            makeNotebookFit: function makeNotebookFit(pane){
                this.notebook = $('#notebook')[0];
                this.notebook.css('width','-='+pane.style.width);
                this.notebook.style.left = 0;
            },

            handleMessage: function handleMessage(message,buffers){
                this.messages.push(message);
                if(message.event=='function_call'){
                    this.handleFunctionCall(message);}
            },

            handleFunctionCall: function handleFunctionCall(event) {
                //TODO: handle exceptions
                //console.log('MolViz3DBaseWidget received a function call: '
                //    + event.function_name +'('+ event.arguments+')');
                //try {
                this.messages.push(event);
                var my_function = this.viewer[event.function_name];
                var result = my_function.apply(this.viewer, event.arguments);

                try { // a hack to prevent circular references
                    if (DONOTSEND.indexOf(result.constructor.name) > -1) {
                        result = result.constructor.name;
                    }
                }
                catch(err){ /* do nothing */ }

                this.send({
                    call_id: event.call_id,
                    result: result, function_name: event.function_name,
                    event: 'function_done'
                });
                /*} catch(e) {
                    console.log(e);
                    this.send({
                        call_id: event.call_id,
                        result: 'error',
                        exception: e,
                        function_name: event.function_name,
                        event: 'function_done'
                    })

                }*/
            }

        });//MolViz3DBaseWidget extension

        return {MolViz3DBase: MolViz3DBase};
    });
