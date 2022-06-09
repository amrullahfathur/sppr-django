d3.contextMenu = function (menu, openCallback) {

	// create the div element that will hold the context menu
	d3.selectAll('.d3-context-menu').data([1])
		.enter()
		.append('div')
		.attr('class', 'd3-context-menu');

	// close menu
	d3.select('body').on('click.d3-context-menu', function() {
		d3.select('.d3-context-menu').style('display', 'none');
	});

	// this gets executed when a contextmenu event occurs
	return function(data, index) {
		var elm = this;

		d3.selectAll('.d3-context-menu').html('');
		var list = d3.selectAll('.d3-context-menu').append('ul');
		list.selectAll('li').data(menu).enter()
			.append('li')
			.html(function(d) {
				let html = ""
				const id = d.title.split(" ")[0]
				switch (id) {
					case "Buat":
						html = `<i class="fa-solid fa-plus"></i> Buat Child Isu Baru`
						break;
					case "Edit":
						html = `<i class="fa-solid fa-pencil"></i> Edit Isu`
						break;
					case "Lihat":
						html = `<i class="fa-solid fa-eye"></i> Lihat Data Pendukung Isu`
						break;
					default:
						html = `<i class="fa-solid fa-trash-can"></i> Hapus Isu`
						break;
				}
				return html;
			})
			.attr('class', function(d) {
				const id = d.title.split(" ")[0]
				switch (id) {
					case "Hapus":
						return "disabled"
				}
			})
			.on('click', function(d, i) {
				d.action(elm, data, index);
				d3.select('.d3-context-menu').style('display', 'none');
			})

		// the openCallback allows an action to fire before the menu is displayed
		// an example usage would be closing a tooltip
		if (openCallback) {
			if (openCallback(data, index) === false) {
				return;
			}
		}

		// display context menu
		d3.select('.d3-context-menu')
			.style('left', (d3.event.pageX - 2) + 'px')
			.style('top', (d3.event.pageY - 2) + 'px')
			.style('display', 'block');

		d3.event.preventDefault();
		d3.event.stopPropagation();
	};
};