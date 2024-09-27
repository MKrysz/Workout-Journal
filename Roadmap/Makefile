
.build/roadmap.mmd: roadmap.toml
	@mkdir -p .build
	@touch .build/roadmap.mmd
	skillmap ./roadmap.toml > .build/roadmap.mmd

.build/roadmap.svg : .build/roadmap.mmd
	mmdc -i .build/roadmap.mmd -o .build/roadmap.png

roadmap: .build/roadmap.svg

make clean:
	rm -rf .build