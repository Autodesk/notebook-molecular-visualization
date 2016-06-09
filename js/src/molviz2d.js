/**
 * Copyright 2016 Autodesk Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var widgets = require('jupyter-js-widgets');
var _ = require('underscore');
d3 = require('./d3.v3.min');

function defaultVal(test,defval){
    if(typeof(test) == 'undefined'){return defval}
    else{return test}}


var MolWidget2DModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
        _model_name : 'MolWidget2DModel',
        _view_name : 'MolWidget2DView',
        _model_module : 'nbmolviz-js',
        _view_module : 'nbmolviz-js'
    })
});

var MolWidget2DView = widgets.DOMWidgetView.extend({

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
        var my_function = this[event.function_name];
        var result = my_function.apply(this, event.arguments);
        this.send({
            call_id: event.call_id,
            result: result, function_name: event.function_name,
            event: 'function_done'
        })},

    render: function render(){
        document.last_2d_widget = this;

        //set properties
        this.width = this.model.get('width');
        this.height = this.model.get('height');
        this.id = this.model.get('uuid');
        this.charge = this.model.get('charge');
        this.graph = this.model.get('graph');

        //create the div
        this.mydiv = document.createElement('div');
        this.mydiv.id = this.id;
        this.mydiv.style.width = this.width;
        this.mydiv.style.height = this.height;
        this.mydiv.style.position = 'relative';

        //Place it
        this.$el.append(this.mydiv);

        //render it
        this.setCss();
        this.renderViewer();
        this.indexSvgElements();

        //set up interactions with python
        this.messages = [];
        this.highlightedAtoms = [];
        this.listenTo(this.model,'msg:custom',
            this.handleMessage,this);
        this.send({'event':'ready'});
            console.log(this.viewerId+' is ready');
    },

    updateHighlightAtoms: function updateHighlightAtoms(atoms){
        var svgAtoms = this.svgNodes;
        this.highlightedAtoms.forEach( function(x){
            svgAtoms[x].style.stroke=null;});
        this.highlightedAtoms = atoms;
        atoms.forEach(function(x){svgAtoms[x].style.stroke='#39F8FF';});
    },

    setCss: function setCss() {
        if($('#graph_css_style'.length>0)) { return }
        var css = ".link line {stroke: #696969;} \n " +
            ".link line.separator {stroke: #fff; stroke-width: 2px;} \n" +
            ".node text {font: 10px sans-serif;  pointer-events: none;}";
        var graphstyle = document.createElement('style');
        graphstyle.type = 'text/css';
        graphstyle.id = 'graph_css_style';
        graphstyle.innerHTML = css;
        document.getElementsByTagName('head')[0].appendChild(style);
    },

    setAtomStyle: function setAtomStyle(atoms,atomSpec){
        this.applyStyleSpec(atoms,this.svgNodes,atomSpec);
    },

    setBondStyle: function setBondStyle(bonds,bondSpec){
        this.applyStyleSpec(bonds,this.svgLinks,bondSpec);
    },

    applyStyleSpec: function applyStyleSpec(objs,objLookup,spec){
        //TODO: don't just assume children[0]
        objs.forEach(function(o){
            var obj = objLookup[o];
            if(typeof(obj)=='undefined'){
                console.log('no object '+o);
                return;
            }
            Object.keys(spec).forEach(function(st){
                obj.children[0].style[st] = spec[st];
            })})
    },

    setAtomLabel: function setAtomLabel(atom,text,spec){
        var obj = this.svgNodes[atom].children[1];
        if(typeof(text) != 'undefined'){
            obj.innerHTML = text;
        }
        Object.keys(spec).forEach(function(st){
                obj.style[st] = spec[st];
            })
    },

    setBondLabel: function setBondLabel(bond,text,spec){
        var link = this.svgLinks[bond];
        if(typeof(link) == 'undefined'){
            console.log('No bond '+bond);
            return;
        }
        if(typeof(text) != 'undefined'){
            link.children[1].innerHTML = text;
        }
        Object.keys(spec).forEach(function(st){
            link.children[1].style[st] = spec[st];
        })
    },

    indexSvgElements:function indexSvgElements(){
        this.svgNodes = {};
        this.svgLinks = {};
        var svgElements = this.svg[0][0].children;
        for(var i=0; i<svgElements.length; ++i){
            var elem = svgElements[i];
            if (elem.getAttribute('class') == 'node'){
                var index = elem.getAttribute('index');
                this.svgNodes[index] = elem;
            }
            if (elem.getAttribute('class') == 'link'){
                var child = elem.children[0];
                var source = child.getAttribute('source');
                var target = child.getAttribute('target');
                this.svgLinks[[source,target]] = elem;
                this.svgLinks[[target,source]] = elem;

            }
        }
    },


    renderViewer:function renderViewer() {
        var width = this.width;
        var height = this.height;

        var colorPicker = d3.scale.category20();

        var mywidget = this;
        function atomClickCallback(){
            mywidget.model.set('clicked_atom_index',
                this.attributes.index.value*1);
            mywidget.model.save();
        }
        function bondClickCallback(){ //not hooked up yet
            mywidget.model.set('clicked_bond_indices',
                [this.attributes.sourceIndex.value*1,
                    this.attributes.targetIndex.value*1]);
            mywidget.model.save();
        }

        function chooseColor(d,defaultVal){
            if(d.category){return colorPicker(d.category);}
            else if(d.color){return d.color;}
            else{return defaultVal;}}

        var radius = d3.scale.sqrt()
            .range([0, 6]);

        var svg = d3.select(this.mydiv).append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("border",1);
        this.svg = svg;

        var borderPath = svg.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("height", height)
            .attr("width", width)
            .style("stroke", "black")
            .style("fill", "none")
            .style("stroke-width", 1);

        var force = d3.layout.force()
            .size([width, height])
            .charge(this.charge)
            .linkDistance(function(d) { return defaultVal(d.distance,20); })
            .linkStrength(function(d) { return defaultVal(d.strength,1.0); });

        var graph = this.graph;

        force
            .nodes(graph.nodes)
            .links(graph.links)
            .on("tick", tick)
            .start();

        this.force = force;

        var link = svg.selectAll(".link")
            .data(graph.links)
            .enter().append("g")
            .attr("class", "link");

        function bondWidth(d) {
            return d.bond*4-2 + "px"; }
        function whiteWidth(d) {
            return d.bond*4-5 + "px"; }

        link.append("line")
            .attr('source',function (d){return d.source.index;})
            .attr('target',function (d){return d.target.index;})
            .style("stroke-width", bondWidth)
            .style("stroke-dasharray", function(d){
                if(d.style=='dashed'){return 5;}
                else{return 0;}})
            .style("stroke", function(d){
                return chooseColor(d,'black')})
            .style("opacity", function(d) {
                if(d.bond!=0){return undefined;}
                else{return 0.0;}});

        link.append("text")
            .attr('x', function(d) { return d.source.x; })
            .attr('y', function(d) { return d.source.y; })
            .attr('text-anchor', 'middle')
            .text(function(d) { return ' '; });

        link.filter(function(d) { return d.bond > 1; }).append("line")
            .attr("class", "separator")
            .style("stroke","#FFF")
            .style("stroke-width",whiteWidth);

        var node = svg.selectAll(".node")
            .data(graph.nodes)
            .enter().append("g")
            .on('click',atomClickCallback)
            .attr("class", "node")
            .attr("index", function(d){return d.index})
            .call(force.drag);

        node.append("circle")
            .attr("r", function(d) {
                return radius(defaultVal(d.size,1.5))})
            .style("fill", function(d){
                return chooseColor(d,'white'); });

        node.append("text")
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .style("color", function(d){
                defaultVal(d.textcolor,'black')})
            .text(function(d) { return d.atom; });

        function tick() {
            link.selectAll("line")
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            link.selectAll("text")
                .attr('x', function(d) {
                    return (d.source.x+d.target.x)/2.0; })
                .attr('y', function(d) {
                    return (d.source.y+d.target.y)/2.0; });

            node.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")"; });

        }
    }});



module.exports = {
    MolWidget2DModel : MolWidget2DModel,
    MolWidget2DView : MolWidget2DView
};
